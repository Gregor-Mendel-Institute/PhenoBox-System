// tslint:disable
// graphql typescript definitions

declare namespace GQL {
  interface IGraphQLResponseRoot {
    data?: IQuery | IMutation;
    errors?: Array<IGraphQLResponseError>;
  }

  interface IGraphQLResponseError {
    /** Required for all errors */
    message: string;
    locations?: Array<IGraphQLResponseErrorLocation>;

    /** 7.2.2 says 'GraphQL servers may provide additional entries to error' */
    [propName: string]: any;
  }

  interface IGraphQLResponseErrorLocation {
    line: number;
    column: number;
  }

  interface IQuery {
    __typename: "Query";

    /**
     * The ID of the object
     */
    node: Node | null;

    /**
     * The ID of the object
     */
    experiment: IExperiment | null;

    /**
     * The ID of the object
     */
    plant: IPlant | null;

    /**
     * The ID of the object
     */
    sampleGroup: ISampleGroup | null;

    /**
     * The ID of the object
     */
    snapshot: ISnapshot | null;

    /**
     * The ID of the object
     */
    timestamp: ITimestamp | null;

    /**
     * The ID of the object
     */
    image: IImage | null;

    /**
     * The ID of the object
     */
    analysis: IAnalysis | null;

    /**
     * The ID of the object
     */
    postprocess: IPostprocess | null;
    postprocessingTask: ITask | null;
    analysisTask: ITask | null;
    analysisJob: IJob | null;
    postprocessingJob: IJob | null;
    experiments: IExperimentConnection | null;
    plants: IPlantConnection | null;
    sampleGroups: ISampleGroupConnection | null;
    snapshots: ISnapshotConnection | null;
    timestamps: ITimestampConnection | null;
    images: IImageConnection | null;
    analyses: IAnalysisConnection | null;
    postprocessings: IPostprocessConnection | null;
    postprocessingStacks: IPostprocessingStackConnection | null;
    pipelines: IPipelineConnection | null;
    analysisTasks: ITaskConnection | null;
    postprocessingTasks: ITaskConnection | null;
  }

  interface INodeOnQueryArguments {
    id: string;
  }

  interface IExperimentOnQueryArguments {
    id: string;
  }

  interface IPlantOnQueryArguments {
    id: string;
  }

  interface ISampleGroupOnQueryArguments {
    id: string;
  }

  interface ISnapshotOnQueryArguments {
    id: string;
  }

  interface ITimestampOnQueryArguments {
    id: string;
  }

  interface IImageOnQueryArguments {
    id: string;
  }

  interface IAnalysisOnQueryArguments {
    id: string;
  }

  interface IPostprocessOnQueryArguments {
    id: string;
  }

  interface IPostprocessingTaskOnQueryArguments {
    id: string;
  }

  interface IAnalysisTaskOnQueryArguments {
    id: string;
  }

  interface IAnalysisJobOnQueryArguments {
    id: string;
  }

  interface IPostprocessingJobOnQueryArguments {
    id: string;
  }

  interface IExperimentsOnQueryArguments {
    withName?: string | null;
    withScientist?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPlantsOnQueryArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISampleGroupsOnQueryArguments {
    forTimestamp?: string | null;
    forAnalysis?: string | null;
    forPostprocess?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISnapshotsOnQueryArguments {
    forTimestamp?: string | null;
    withCameraPosition?: string | null;
    withMeasurementTool?: string | null;
    forOpenTimestamp?: boolean | null;
    forPlant?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ITimestampsOnQueryArguments {
    forExperiment?: string | null;
    ordered?: boolean | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IImagesOnQueryArguments {
    forSnapshot?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IAnalysesOnQueryArguments {
    forTimestamp?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessingsOnQueryArguments {
    forAnalysis?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessingStacksOnQueryArguments {
    unusedForAnalysis?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPipelinesOnQueryArguments {
    unusedForTimestamp?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IAnalysisTasksOnQueryArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessingTasksOnQueryArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  /**
   * An object with an ID
   */
  type Node = IExperiment | ISampleGroup | IPlant | ISnapshot | ITimestamp | IAnalysis | IPostprocess | IImage;

  /**
   * An object with an ID
   */
  interface INode {
    __typename: "Node";

    /**
     * The ID of the object.
     */
    id: string;
  }

  interface IExperiment {
    __typename: "Experiment";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    name: string | null;
    description: string | null;
    scientist: string | null;
    groupName: string | null;
    startDate: any | null;
    startOfExperimentation: any | null;
    sampleGroups: ISampleGroupConnection | null;
    timestamps: ITimestampConnection | null;
  }

  interface ISampleGroupsOnExperimentArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ITimestampsOnExperimentArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISampleGroupConnection {
    __typename: "SampleGroupConnection";
    pageInfo: IPageInfo;
    edges: Array<ISampleGroupEdge>;
  }

  interface IPageInfo {
    __typename: "PageInfo";

    /**
     * When paginating forwards, are there more items?
     */
    hasNextPage: boolean;

    /**
     * When paginating backwards, are there more items?
     */
    hasPreviousPage: boolean;

    /**
     * When paginating backwards, the cursor to continue.
     */
    startCursor: string | null;

    /**
     * When paginating forwards, the cursor to continue.
     */
    endCursor: string | null;
  }

  interface ISampleGroupEdge {
    __typename: "SampleGroupEdge";

    /**
     * The item at the end of the edge
     */
    node: ISampleGroup | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface ISampleGroup {
    __typename: "SampleGroup";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    name: string;
    description: string | null;
    species: string | null;
    genotype: string | null;
    variety: string | null;
    growthConditions: string | null;
    treatment: string | null;
    isControl: boolean;
    experimentId: number;
    experiment: IExperiment | null;
    plants: IPlantConnection | null;
  }

  interface IPlantsOnSampleGroupArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPlantConnection {
    __typename: "PlantConnection";
    pageInfo: IPageInfo;
    edges: Array<IPlantEdge>;
  }

  interface IPlantEdge {
    __typename: "PlantEdge";

    /**
     * The item at the end of the edge
     */
    node: IPlant | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IPlant {
    __typename: "Plant";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    name: string | null;
    index: number | null;
    sampleGroupId: number | null;
    sampleGroup: ISampleGroup | null;
    snapshots: ISnapshotConnection | null;
    fullName: string | null;
  }

  interface ISnapshotsOnPlantArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISnapshotConnection {
    __typename: "SnapshotConnection";
    pageInfo: IPageInfo;
    edges: Array<ISnapshotEdge>;
  }

  interface ISnapshotEdge {
    __typename: "SnapshotEdge";

    /**
     * The item at the end of the edge
     */
    node: ISnapshot | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface ISnapshot {
    __typename: "Snapshot";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    measurementTool: string | null;
    phenoboxId: string;
    cameraPosition: string;
    excluded: boolean;
    timestampId: number;
    plantId: number;
    timestamp: ITimestamp | null;
    plant: IPlant | null;
    postprocesses: IPostprocessConnection | null;
    images: IImageConnection | null;
    analyses: IAnalysisConnection | null;
  }

  interface IPostprocessesOnSnapshotArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IImagesOnSnapshotArguments {
    withType?: string | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IAnalysesOnSnapshotArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ITimestamp {
    __typename: "Timestamp";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    iapExpId: string | null;
    completed: boolean;
    experimentId: number;
    experiment: IExperiment | null;
    snapshots: ISnapshotConnection | null;
    analyses: IAnalysisConnection | null;
  }

  interface ISnapshotsOnTimestampArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IAnalysesOnTimestampArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IAnalysisConnection {
    __typename: "AnalysisConnection";
    pageInfo: IPageInfo;
    edges: Array<IAnalysisEdge>;
  }

  interface IAnalysisEdge {
    __typename: "AnalysisEdge";

    /**
     * The item at the end of the edge
     */
    node: IAnalysis | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IAnalysis {
    __typename: "Analysis";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    iapId: string | null;
    exportPath: string | null;
    pipelineId: string;
    startedAt: any | null;
    finishedAt: any | null;
    timestampId: number;
    timestamp: ITimestamp | null;
    postprocessings: IPostprocessConnection | null;
    sampleGroups: ISampleGroupConnection | null;
    pipeline: IPipeline | null;
    snapshots: ISnapshotConnection | null;
  }

  interface IPostprocessingsOnAnalysisArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISampleGroupsOnAnalysisArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISnapshotsOnAnalysisArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessConnection {
    __typename: "PostprocessConnection";
    pageInfo: IPageInfo;
    edges: Array<IPostprocessEdge>;
  }

  interface IPostprocessEdge {
    __typename: "PostprocessEdge";

    /**
     * The item at the end of the edge
     */
    node: IPostprocess | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IPostprocess {
    __typename: "Postprocess";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    snapshotHash: number;
    resultPath: string | null;
    postprocessingStackId: string;
    controlGroupId: number;
    startedAt: any | null;
    finishedAt: any | null;
    note: string | null;
    analysisId: number;
    analysis: IAnalysis | null;
    snapshots: ISnapshotConnection | null;
    controlGroup: ISampleGroup | null;
    sampleGroups: ISampleGroupConnection | null;
    postprocessingStack: IPostprocessingStack | null;
  }

  interface ISnapshotsOnPostprocessArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface ISampleGroupsOnPostprocessArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessingStack {
    __typename: "PostprocessingStack";
    id: string | null;
    name: string | null;
    description: string | null;
    scripts: IPostprocessingScriptConnection | null;
  }

  interface IScriptsOnPostprocessingStackArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IPostprocessingScriptConnection {
    __typename: "PostprocessingScriptConnection";
    pageInfo: IPageInfo;
    edges: Array<IPostprocessingScriptEdge>;
  }

  interface IPostprocessingScriptEdge {
    __typename: "PostprocessingScriptEdge";

    /**
     * The item at the end of the edge
     */
    node: IPostprocessingScript | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IPostprocessingScript {
    __typename: "PostprocessingScript";
    id: string | null;
    name: string | null;
    index: number | null;
    description: string | null;
  }

  interface IPipeline {
    __typename: "Pipeline";
    id: string | null;
    name: string | null;
    description: string | null;
  }

  interface IImageConnection {
    __typename: "ImageConnection";
    pageInfo: IPageInfo;
    edges: Array<IImageEdge>;
  }

  interface IImageEdge {
    __typename: "ImageEdge";

    /**
     * The item at the end of the edge
     */
    node: IImage | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IImage {
    __typename: "Image";

    /**
     * The ID of the object.
     */
    id: string;
    createdAt: any | null;
    updatedAt: any | null;
    path: string;
    filename: string;
    type: string;
    angle: number;
    snapshotId: number;
    snapshot: ISnapshot | null;
  }

  interface ITimestampConnection {
    __typename: "TimestampConnection";
    pageInfo: IPageInfo;
    edges: Array<ITimestampEdge>;
  }

  interface ITimestampEdge {
    __typename: "TimestampEdge";

    /**
     * The item at the end of the edge
     */
    node: ITimestamp | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface ITask {
    __typename: "Task";
    id: string | null;
    name: string | null;
    description: string | null;
    taskType: TaskType | null;
    currentStatus: TaskState | null;
    currentMessage: string | null;
    jobs: IJobConnection | null;
  }

  interface IJobsOnTaskArguments {
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  enum TaskType {
    ANALYSIS = 'ANALYSIS',
    POSTPROCESS = 'POSTPROCESS'
  }

  enum TaskState {
    CREATED = 'CREATED',
    QUEUED = 'QUEUED',
    RUNNING = 'RUNNING',
    FINISHED = 'FINISHED',
    FAILED = 'FAILED'
  }

  interface IJobConnection {
    __typename: "JobConnection";
    pageInfo: IPageInfo;
    edges: Array<IJobEdge>;
  }

  interface IJobEdge {
    __typename: "JobEdge";

    /**
     * The item at the end of the edge
     */
    node: IJob | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IJob {
    __typename: "Job";
    id: string | null;
    name: string | null;
    description: string | null;
    status: string | null;
    enqueuedAt: string | null;
    startedAt: string | null;
    finishedAt: string | null;
    log: IStatusLogEntryConnection | null;
  }

  interface ILogOnJobArguments {
    newestFirst?: boolean | null;
    before?: string | null;
    after?: string | null;
    first?: number | null;
    last?: number | null;
  }

  interface IStatusLogEntryConnection {
    __typename: "StatusLogEntryConnection";
    pageInfo: IPageInfo;
    edges: Array<IStatusLogEntryEdge>;
    totalCount: number;
  }

  interface IStatusLogEntryEdge {
    __typename: "StatusLogEntryEdge";

    /**
     * The item at the end of the edge
     */
    node: IStatusLogEntry | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IStatusLogEntry {
    __typename: "StatusLogEntry";
    id: string | null;
    timestamp: string | null;
    message: string | null;
    progress: number | null;
  }

  interface IExperimentConnection {
    __typename: "ExperimentConnection";
    pageInfo: IPageInfo;
    edges: Array<IExperimentEdge>;
  }

  interface IExperimentEdge {
    __typename: "ExperimentEdge";

    /**
     * The item at the end of the edge
     */
    node: IExperiment | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IPostprocessingStackConnection {
    __typename: "PostprocessingStackConnection";
    pageInfo: IPageInfo;
    edges: Array<IPostprocessingStackEdge>;
  }

  interface IPostprocessingStackEdge {
    __typename: "PostprocessingStackEdge";

    /**
     * The item at the end of the edge
     */
    node: IPostprocessingStack | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IPipelineConnection {
    __typename: "PipelineConnection";
    pageInfo: IPageInfo;
    edges: Array<IPipelineEdge>;
  }

  interface IPipelineEdge {
    __typename: "PipelineEdge";

    /**
     * The item at the end of the edge
     */
    node: IPipeline | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface ITaskConnection {
    __typename: "TaskConnection";
    pageInfo: IPageInfo;
    edges: Array<ITaskEdge>;
  }

  interface ITaskEdge {
    __typename: "TaskEdge";

    /**
     * The item at the end of the edge
     */
    node: ITask | null;

    /**
     * A cursor for use in pagination
     */
    cursor: string;
  }

  interface IMutation {
    __typename: "Mutation";
    constructExperiment: IConstructExperiment | null;
    createExperiment: ICreateExperiment | null;
    createSampleGroup: ICreateSampleGroup | null;
    createPlant: ICreatePlant | null;
    createSnapshot: ICreateSnapshot | null;
    completeTimestamp: ICompleteTimestamp | null;
    addImage: IAddImage | null;
    editProject: IEditProject | null;
    changeSnapshotExclusion: IChangeSnapshotExclusion | null;
    deleteExperiment: IDeleteExperiment | null;
    deletePlant: IDeletePlant | null;
    deleteSampleGroup: IDeleteSampleGroup | null;
    deleteSnapshot: IDeleteSnapshot | null;
  }

  interface IConstructExperimentOnMutationArguments {
    experimentData?: IExperimentInput | null;
  }

  interface ICreateExperimentOnMutationArguments {
    description?: string | null;
    scientist?: string | null;
    name?: string | null;
    groupName?: string | null;
  }

  interface ICreateSampleGroupOnMutationArguments {
    groupData?: ISampleGroupInput | null;
    experimentId: string;
  }

  interface ICreatePlantOnMutationArguments {
    index?: number | null;
    name?: string | null;
    sampleGroupId?: number | null;
  }

  interface ICreateSnapshotOnMutationArguments {
    measurementTool: string;
    phenoboxId: string;
    cameraPosition: string;
    plantId: string;
  }

  interface ICompleteTimestampOnMutationArguments {
    timestampId: string;
  }

  interface IAddImageOnMutationArguments {
    path: string;
    type?: string | null;
    snapshotId: string;
    angle: number;
    filename: string;
  }

  interface IEditProjectOnMutationArguments {
    projectData?: IEditProjectInput | null;
  }

  interface IChangeSnapshotExclusionOnMutationArguments {
    exclude: boolean;
    snapshotId: string;
  }

  interface IDeleteExperimentOnMutationArguments {
    id?: string | null;
  }

  interface IDeletePlantOnMutationArguments {
    id?: string | null;
  }

  interface IDeleteSampleGroupOnMutationArguments {
    id?: string | null;
  }

  interface IDeleteSnapshotOnMutationArguments {
    id?: string | null;
  }

  interface IExperimentInput {
    name: string;
    description?: string | null;
    scientist: string;
    groupName: string;
    startDate?: string | null;
    startOfExperimentation?: string | null;
    sampleGroupData?: Array<ISampleGroupInput> | null;
  }

  interface ISampleGroupInput {
    name: string;
    description?: string | null;
    treatment: string;
    species?: string | null;
    genotype?: string | null;
    variety?: string | null;
    growthConditions?: string | null;
    isControl?: boolean | null;
    plants?: Array<IPlantInput> | null;
  }

  interface IPlantInput {
    index: number;
    name: string;
  }

  interface IConstructExperiment {
    __typename: "ConstructExperiment";
    id: string | null;
  }

  interface ICreateExperiment {
    __typename: "CreateExperiment";
    id: number | null;
    name: string | null;
    description: string | null;
    scientist: string | null;
    groupName: string | null;
    startDate: string | null;
    startOfExperimentation: string | null;
  }

  interface ICreateSampleGroup {
    __typename: "CreateSampleGroup";
    id: number | null;
    name: string | null;
    description: string | null;
    treatment: string | null;
    species: string | null;
    genotype: string | null;
    variety: string | null;
    growthConditions: string | null;
    isControl: boolean | null;
    experimentId: number | null;
  }

  interface ICreatePlant {
    __typename: "CreatePlant";
    id: number | null;
    index: number | null;
    name: string | null;
    sampleGroupId: number | null;
  }

  interface ICreateSnapshot {
    __typename: "CreateSnapshot";
    id: string | null;
    timestampId: string | null;
  }

  interface ICompleteTimestamp {
    __typename: "CompleteTimestamp";
    id: string | null;
  }

  interface IAddImage {
    __typename: "AddImage";
    id: string | null;
  }

  interface IEditProjectInput {
    id: string;
    name?: string | null;
    description?: string | null;
    scientist?: string | null;
    groupName?: string | null;
    startDate?: string | null;
    startOfExperimentation?: string | null;
    sampleGroupData?: Array<IEditSampleGroupInput> | null;
  }

  interface IEditSampleGroupInput {
    id: string;
    name?: string | null;
    description?: string | null;
    isControl?: boolean | null;
    treatment: string;
    species?: string | null;
    genotype?: string | null;
    variety?: string | null;
    growthConditions?: string | null;
    plants?: Array<IEditPlantInput> | null;
    delete?: boolean | null;
  }

  interface IEditPlantInput {
    id: string;
    index?: number | null;
    name?: string | null;
    delete?: boolean | null;
  }

  interface IEditProject {
    __typename: "EditProject";
    experiment: IExperiment | null;
  }

  interface IChangeSnapshotExclusion {
    __typename: "ChangeSnapshotExclusion";
    id: string | null;
    excluded: boolean | null;
  }

  interface IDeleteExperiment {
    __typename: "DeleteExperiment";
    id: string | null;
  }

  interface IDeletePlant {
    __typename: "DeletePlant";
    id: string | null;
  }

  interface IDeleteSampleGroup {
    __typename: "DeleteSampleGroup";
    id: string | null;
  }

  interface IDeleteSnapshot {
    __typename: "DeleteSnapshot";
    id: string | null;
  }
}

// tslint:enable

