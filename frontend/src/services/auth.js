import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from "amazon-cognito-identity-js";
import { awsConfig } from "../config/aws";

const userPool = new CognitoUserPool({
  UserPoolId: awsConfig.userPoolId,
  ClientId: awsConfig.clientId,
});

export function signUp(email, password, role) {
  return new Promise((resolve, reject) => {
    const attributes = [
      new CognitoUserAttribute({ Name: "email", Value: email }),
      new CognitoUserAttribute({ Name: "custom:user_role", Value: role }),
    ];

    userPool.signUp(email, password, attributes, null, (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
}

export function signIn(email, password) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({ Username: email, Pool: userPool });
    const authDetails = new AuthenticationDetails({
      Username: email,
      Password: password,
    });

    user.authenticateUser(authDetails, {
      onSuccess: (session) => resolve(session),
      onFailure: (err) => reject(err),
    });
  });
}

export function signOut() {
  const user = userPool.getCurrentUser();
  if (user) user.signOut();
}

export function getCurrentUser() {
  return new Promise((resolve, reject) => {
    const user = userPool.getCurrentUser();
    if (!user) return resolve(null);

    user.getSession((err, session) => {
      if (err || !session.isValid()) return resolve(null);

      user.getUserAttributes((err, attributes) => {
        if (err) return reject(err);

        const attrs = {};
        attributes.forEach((attr) => {
          attrs[attr.getName()] = attr.getValue();
        });

        resolve({
          id: attrs["sub"],
          email: attrs["email"],
          role: attrs["custom:user_role"],
          session,
        });
      });
    });
  });
}

export function getToken() {
  return new Promise((resolve, reject) => {
    const user = userPool.getCurrentUser();
    if (!user) return resolve(null);

    user.getSession((err, session) => {
      if (err) return reject(err);
      resolve(session.getIdToken().getJwtToken());
    });
  });
}
