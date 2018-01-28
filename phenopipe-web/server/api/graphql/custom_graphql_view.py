from flask_graphql import GraphQLView

from server.api.exceptions import ForbiddenActionError
from server.api.graphql.exceptions import ConstraintViolationError, InvalidMutationRequestError, UnableToDeleteError, \
    UnknownDataError, ConflictingDataError
from server.modules.processing.remote_exceptions import UnavailableError


class CustomGraphQLView(GraphQLView):
    @staticmethod
    def format_error(error):
        if hasattr(error, 'original_error') and error.original_error:
            formatted = {"message": str(error.original_error)}
            if isinstance(error.original_error, UnavailableError):
                formatted['code'] = 503
            elif isinstance(error.original_error, ForbiddenActionError):
                formatted['code'] = 403
            elif isinstance(error.original_error, ConstraintViolationError):
                formatted['code'] = 422
            elif isinstance(error.original_error, ConflictingDataError):
                formatted['code'] = 409
            elif isinstance(error.original_error, InvalidMutationRequestError):
                formatted['code'] = 422
            elif isinstance(error.original_error, UnableToDeleteError):
                formatted['code'] = 422
            elif isinstance(error.original_error, UnknownDataError):
                formatted['code'] = 500
            return formatted

        return GraphQLView.format_error(error)
