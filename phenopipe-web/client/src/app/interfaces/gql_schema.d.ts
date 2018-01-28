// tslint:disable
// graphql typescript definitions

declare namespace GQL {
  interface IGraphQLResponseRoot {
    data?: IQuery | IMutation;
    errors?: Array<IGraphQLResponseError>;
  }

  interface IGraphQLResponseError {
    message: string;            // Required for all errors
    locations?: Array<IGraphQLResponseErrorLocation>;
    [propName: string]: any;    // 7.2.2 says 'GraphQL servers may provide additional entries to error'
  }

  interface IGraphQLResponseErrorLocation {
    line: number;
    column: number;
  }


  interface IQuery {
    __typename: "Query";
    /**
    description: The ID of the object
  */
    node: Node | null;
    /**
    description: The ID of the object
  */
    experiment: IExperiment | null;
    /**
    description: The ID of the object
  */
    plant: IPlant | null;
    /**
    description: The ID of the object
  */
    sampleGroup: ISampleGroup | null;
    /**
    description: The ID of the object
  */
    snapshot: ISnapshot | null;
    /**
    description: The ID of the object
  */
    timestamp: ITimestamp | null;
    /**
    description: The ID of the object
  */
    image: IImage | null;
    /**
    description: The ID of the object
  */
    analysis: IAnalysis | null;
    /**
    description: The ID of the object
  */
    postprocess: IPostprocess | null;
    postprocessingTaskStatus: ITaskStatus | null;
    analysisTaskStatus: ITaskStatus | null;
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
    analysisTaskStatuses: ITaskStatusConnection | null;
    postprocessingTaskStatuses: ITaskStatusConnection | null;
  }

  /**
    description: An object with an ID
  */
  type Node = IExperiment | ISampleGroup | IPlant | ISnapshot | ITimestamp | IAnalysis | IPostprocess | IImage;

  /**
    description: An object with an ID
  */
  interface INode {
    __typename: "Node";
    /**
    description: The ID of the object.
  */
    id: string;
  }


  interface IExperiment {
    __typename: "Experiment";
    /**
    description: The ID of the object.
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


  interface ISampleGroupConnection {
    __typename: "SampleGroupConnection";
    pageInfo: IPageInfo;
    edges: Array<ISampleGroupEdge>;
  }


  interface IPageInfo {
    __typename: "PageInfo";
    /**
    description: When paginating forwards, are there more items?
  */
    hasNextPage: boolean;
    /**
    description: When paginating backwards, are there more items?
  */
    hasPreviousPage: boolean;
    /**
    description: When paginating backwards, the cursor to continue.
  */
    startCursor: string | null;
    /**
    description: When paginating forwards, the cursor to continue.
  */
    endCursor: string | null;
  }


  interface ISampleGroupEdge {
    __typename: "SampleGroupEdge";
    /**
    description: The item at the end of the edge
  */
    node: ISampleGroup | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface ISampleGroup {
    __typename: "SampleGroup";
    /**
    description: The ID of the object.
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


  interface IPlantConnection {
    __typename: "PlantConnection";
    pageInfo: IPageInfo;
    edges: Array<IPlantEdge>;
  }


  interface IPlantEdge {
    __typename: "PlantEdge";
    /**
    description: The item at the end of the edge
  */
    node: IPlant | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface IPlant {
    __typename: "Plant";
    /**
    description: The ID of the object.
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


  interface ISnapshotConnection {
    __typename: "SnapshotConnection";
    pageInfo: IPageInfo;
    edges: Array<ISnapshotEdge>;
  }


  interface ISnapshotEdge {
    __typename: "SnapshotEdge";
    /**
    description: The item at the end of the edge
  */
    node: ISnapshot | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface ISnapshot {
    __typename: "Snapshot";
    /**
    description: The ID of the object.
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
    analyses: IAnalysisConnection | null;
    postprocesses: IPostprocessConnection | null;
    images: IImageConnection | null;
  }


  interface ITimestamp {
    __typename: "Timestamp";
    /**
    description: The ID of the object.
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


  interface IAnalysisConnection {
    __typename: "AnalysisConnection";
    pageInfo: IPageInfo;
    edges: Array<IAnalysisEdge>;
  }


  interface IAnalysisEdge {
    __typename: "AnalysisEdge";
    /**
    description: The item at the end of the edge
  */
    node: IAnalysis | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface IAnalysis {
    __typename: "Analysis";
    /**
    description: The ID of the object.
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
    snapshots: ISnapshotConnection | null;
    sampleGroups: ISampleGroupConnection | null;
    pipeline: IPipeline | null;
  }


  interface IPostprocessConnection {
    __typename: "PostprocessConnection";
    pageInfo: IPageInfo;
    edges: Array<IPostprocessEdge>;
  }


  interface IPostprocessEdge {
    __typename: "PostprocessEdge";
    /**
    description: The item at the end of the edge
  */
    node: IPostprocess | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface IPostprocess {
    __typename: "Postprocess";
    /**
    description: The ID of the object.
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


  interface IPostprocessingStack {
    __typename: "PostprocessingStack";
    id: string | null;
    name: string | null;
    description: string | null;
    scripts: IPostprocessingScriptConnection | null;
  }


  interface IPostprocessingScriptConnection {
    __typename: "PostprocessingScriptConnection";
    pageInfo: IPageInfo;
    edges: Array<IPostprocessingScriptEdge>;
  }


  interface IPostprocessingScriptEdge {
    __typename: "PostprocessingScriptEdge";
    /**
    description: The item at the end of the edge
  */
    node: IPostprocessingScript | null;
    /**
    description: A cursor for use in pagination
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
    description: The item at the end of the edge
  */
    node: IImage | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface IImage {
    __typename: "Image";
    /**
    description: The ID of the object.
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
    description: The item at the end of the edge
  */
    node: ITimestamp | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface ITaskStatus {
    __typename: "TaskStatus";
    id: string | null;
    name: string | null;
    description: string | null;
    taskType: ITaskTypeEnum | null;
    currentStatus: IStatusEnum | null;
    currentMessage: string | null;
    jobs: IJobConnection | null;
    log: IStatusLogEntryConnection | null;
  }


  type ITaskTypeEnum = 'analysis' | 'postprocess';


  type IStatusEnum = 'created' | 'pending' | 'running' | 'finished' | 'error';


  interface IJobConnection {
    __typename: "JobConnection";
    pageInfo: IPageInfo;
    edges: Array<IJobEdge>;
  }


  interface IJobEdge {
    __typename: "JobEdge";
    /**
    description: The item at the end of the edge
  */
    node: IJob | null;
    /**
    description: A cursor for use in pagination
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
    description: The item at the end of the edge
  */
    node: IStatusLogEntry | null;
    /**
    description: A cursor for use in pagination
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
    description: The item at the end of the edge
  */
    node: IExperiment | null;
    /**
    description: A cursor for use in pagination
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
    description: The item at the end of the edge
  */
    node: IPostprocessingStack | null;
    /**
    description: A cursor for use in pagination
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
    description: The item at the end of the edge
  */
    node: IPipeline | null;
    /**
    description: A cursor for use in pagination
  */
    cursor: string;
  }


  interface ITaskStatusConnection {
    __typename: "TaskStatusConnection";
    pageInfo: IPageInfo;
    edges: Array<ITaskStatusEdge>;
  }


  interface ITaskStatusEdge {
    __typename: "TaskStatusEdge";
    /**
    description: The item at the end of the edge
  */
    node: ITaskStatus | null;
    /**
    description: A cursor for use in pagination
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
    ok: boolean | null;
  }


  interface ICompleteTimestamp {
    __typename: "CompleteTimestamp";
    id: string | null;
  }


  interface IAddImage {
    __typename: "AddImage";
    id: string | null;
    ok: boolean | null;
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

