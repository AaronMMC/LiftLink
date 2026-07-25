export const awsConfig = {
  region: import.meta.env.VITE_AWS_REGION || "us-east-1",
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || "",
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID || "",
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:3000",
};
