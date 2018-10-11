import os
import string

import zipstream
from flask import current_app, Response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from graphql_relay import from_global_id

from server.api.blueprints import api
from server.api.exceptions import ForbiddenActionError
from server.extensions import db
from server.models import AnalysisModel, SnapshotModel, ImageModel, TimestampModel
from server.modules.processing.analysis.analysis import get_iap_pipeline
from server.modules.processing.exceptions import InvalidPathError, AnalysisDataNotPresentError
from server.utils.util import get_local_path_from_smb


def _get_local_image_paths(images, shared_folder_map):
    image_paths = list()
    for image in images:
        if image.type == 'raw':
            local_image_path = os.path.dirname(get_local_path_from_smb(image.path, shared_folder_map))
            if local_image_path is None:
                raise InvalidPathError(image.path, 'The stored image location could not be resolved')
            image_paths.append(os.path.join(local_image_path, image.filename))
    return image_paths


def _get_image_paths_for_analysis(analysis, shared_folder_map):
    """
    Consolidates all paths to images, as local paths, of the given analysis into a list

    :param analysis: The :class:`~server.model.analysis_model.AnalysisModel` instance for which the images should be gathered
    :param shared_folder_map: A dict containing a mapping from SMB URLs to local mount points

    :return: A list of full file paths for all images belonging to the given :class:`~server.model.analysis_model.AnalysisModel`
        instance
    """
    raw_images = list()
    segmented_images = list()
    snapshots = analysis.timestamp.snapshots

    for snapshot in snapshots:
        raw_image_path = None
        segmented_image_path = None
        for image in snapshot.images:
            # Assume that all images of the same snapshot reside in the same directory
            if image.type == 'raw':
                if raw_image_path is None:
                    raw_image_path = os.path.dirname(get_local_path_from_smb(image.path, shared_folder_map))
                    if raw_image_path is None:
                        raise InvalidPathError(image.path, 'The stored image location could not be resolved')
                raw_images.append(os.path.join(raw_image_path, image.filename))
            elif image.type == 'segmented':
                if segmented_image_path is None:
                    segmented_image_path = os.path.dirname(get_local_path_from_smb(image.path, shared_folder_map))
                    if segmented_image_path is None:
                        raise InvalidPathError(image.path, 'The stored image location could not be resolved')
                segmented_images.append(os.path.join(segmented_image_path, image.filename))
    return raw_images, segmented_images


def _get_postproccessing_result_paths(analysis, shared_folder_map):
    """
    Consolidates all paths, as local paths, to folders where postprocessing results of the given analysis are stored into a list

    :param analysis: The :class:`~server.model.analysis_model.AnalysisModel` instance
        for which all postprocess result paths should be gathered
    :param shared_folder_map: A dict containing a mapping from SMB URLs to local mount points

    :return: A list of all result paths (as local paths)
    """
    paths = list()
    for postprocess in analysis.postprocessings:
        if postprocess.result_path is not None:
            local_path = get_local_path_from_smb(postprocess.result_path, shared_folder_map)
            if local_path is not None:
                paths.append(local_path)
            else:
                raise InvalidPathError(postprocess.result_path,
                                       'The path to the postprocessing results could not be resolved')
    return paths


def sanitize_string(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    res = ''.join(c for c in s if c in valid_chars)
    res = res.replace(' ', '_')
    return res


# TODO make seperate download blueprint?
@api.route('/download-images', methods=['GET', 'POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def download_images():
    """
    API endpoint for downloading raw images.

    """

    def generator(name, image_paths):
        """
        Creates a generator which yields chunks of a zip file containing the relevant image files.

        :param name: The name of the zip file
        :param image_paths: A list of image paths which should be included

        :return: A generator which yields chunks of the resulting zip file
        """
        z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
        if image_paths is not None:
            for image_path in image_paths:
                arcpath = os.path.join(name, os.path.basename(image_path))
                z.write(image_path, arcpath)

        for chunk in z:
            yield chunk

    timestamp_id = request.get_json()['timestamp_id']
    _, timestamp_db_id = from_global_id(timestamp_id)
    timestamp = db.session.query(TimestampModel).get(timestamp_db_id)
    snapshots = db.session.query(SnapshotModel).filter(SnapshotModel.timestamp_id == timestamp_db_id).all()
    image_paths = []
    shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
    for snapshot in snapshots:
        image_paths.extend(
            _get_local_image_paths(snapshot.images.filter(ImageModel.type == 'raw'), shared_folder_map))
    experiment_name_safe = sanitize_string(timestamp.experiment.name)
    name = '{}_{}'.format('images', experiment_name_safe)
    response = Response(generator(name, image_paths), mimetype='application/zip')

    response.headers['Content-Disposition'] = 'attachment; filename={}_{}{}'.format(name,
                                                                                    timestamp.created_at,
                                                                                    '.zip')
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response


@api.route('/download-results', methods=['GET', 'POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def download_results():
    """
    API endpoint for downloading results as a zip file.

    This endpoint takes an optional argument 'with_pictures' which defaults to False, indicating whether or not
    all corresponding images should be downloaded or not
    """

    def generator(name, analysis, postprocessings, raw_image_paths=list(), segmented_image_paths=list()):
        """
        Creates a generator which yields chunks of a zip file containing the relevant result files.

        :param name: The name of the zip file
        :param analysis: The analysis instance which results should be provided

        :return: A generator which yields chunks of the resulting zip file
        """

        def _traverse_and_write(path, root, arcname):
            for traversal_root, dirs, files in os.walk(path):
                for filename in files:
                    file_path = os.path.join(traversal_root, filename)
                    z.write(file_path, os.path.join(arcname, os.path.relpath(file_path, root)))

        z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
        analysis_result_root = get_local_path_from_smb(analysis.export_path, shared_folder_map)
        root = os.path.abspath(os.path.join(analysis_result_root, os.pardir))
        _traverse_and_write(analysis_result_root, root, name)

        for postprocess in postprocessings:
            if postprocess.result_path is not None:
                local_path = get_local_path_from_smb(postprocess.result_path, shared_folder_map)
                arcpath = os.path.join(name, os.path.relpath(local_path, root))
                z.writestr(os.path.join(arcpath, 'note.txt'), postprocess.note)
                _traverse_and_write(local_path, root, name)

        image_basepath = os.path.join(name, 'images')
        for image_path in raw_image_paths:
            arcpath = os.path.join(image_basepath, 'original', os.path.basename(image_path))
            z.write(image_path, arcpath)
        for image_path in segmented_image_paths:
            arcpath = os.path.join(image_basepath, 'segmented', os.path.basename(image_path))
            z.write(image_path, arcpath)

        for chunk in z:
            yield chunk

    identity = get_jwt_identity()
    analysis_id = request.get_json()['analysis_id']
    with_pictures = request.get_json()['with_pictures']
    if with_pictures is None:
        with_pictures = False
    _, analysis_db_id = from_global_id(analysis_id)
    analysis = db.session.query(AnalysisModel).get(analysis_db_id)
    if identity['username'] == analysis.timestamp.experiment.scientist:
        shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
        if analysis.export_path is None:
            raise AnalysisDataNotPresentError(analysis.id, 'No Exported data available')
        raw_image_paths = list()
        segmented_image_paths = list()
        if with_pictures:
            raw_image_paths, segmented_image_paths = _get_image_paths_for_analysis(analysis, shared_folder_map)

        pipeline = get_iap_pipeline(username=identity.get('username'), pipeline_id=analysis.pipeline_id)
        pipeline_name_safe = sanitize_string(pipeline.name)
        experiment_name_safe = sanitize_string(analysis.timestamp.experiment.name)
        name = '{}_{}_{}'.format('results',
                                 experiment_name_safe,
                                 pipeline_name_safe)

        response = Response(generator(name, analysis, analysis.postprocessings, raw_image_paths, segmented_image_paths),
                            mimetype='application/zip')

        response.headers['Content-Disposition'] = 'attachment; filename={}_{}{}'.format(name,
                                                                                        analysis.timestamp.created_at,
                                                                                        '.zip')
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
    else:
        # TODO inform admin?
        raise ForbiddenActionError('You can only download your own data.', identity['username'])
