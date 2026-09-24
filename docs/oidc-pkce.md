# OIDC Authorization Code + PKCE

The demo clients use this flow:

1. Generate `state`, `nonce`, `code_verifier`.
2. Send `code_challenge = BASE64URL(SHA256(code_verifier))` to Keycloak `/authorize`.
3. User authenticates.
4. Keycloak redirects back with a short-lived authorization code and the original `state`.
5. Client verifies `state`.
6. Client exchanges `code + code_verifier` at `/token`.
7. Keycloak returns ID, access and refresh tokens.
8. Client verifies the returned ID-token `nonce`.

Important distinctions:

- ID token: authentication result for the client.
- Access token: presented to APIs.
- Refresh token: obtains fresh access tokens; protect it more strongly.
- PKCE: prevents a stolen authorization code from being useful without the verifier.
