// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `angular-cli.json`.

export const environment = {
  production                       : false,
  baseUrl                          : "http://localhost:4200/",
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
