export const environment = {
  production                       : true,
  //TODO Use dns name
  baseUrl                          : "http://10.60.64.241:8080/",
  graphqlEndpoint                  : "graphql",
  printEndpoint                    : "api/print",
  iapAnalysisEndpoint              : "api/analyse-timestamp-data-iap",
  postprocessingEndpoint           : "api/postprocess_analysis",
  authEndpoint                     : "auth/auth",
  reauthEndpoint                   : "auth/reauth",
  uploadPostprocessingStackEndpoint: "api/upload-postprocessing-stack",
  uploadIapPipelineEndpoint        : "api/upload-iap-pipeline",
  deleteIapPipelineEndpoint        : "api/delete-iap-pipeline",
  downloadResultsEndpoint          : "api/download-results",
  downloadImagesEndpoint           : "api/download-images",
  plantNameMaxLength               : 16,
  defaultSampleCount               : 10,
};
