import json, pathlib

# The private key from the service account.
# The literal backslash in the base64 key (before 'C') must be a double-backslash in JSON.
private_key = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxw5i4QTStyU2v\n"
    "VuMrP5BjIsAOFaZNwrF0L9KWrgziTui1FPSVkfaczwaW0yCgXy8PX35h6LRA9F/j\n"
    "kz2c3L2TcLl827ntkC1e+T1k5LkQq4lbRIEIcQvmjDUfsTRZqXhZDEowSAC+bBY9\n"
    "4Wl57yx1Z6mJrUUouYHQ58DLsg4Vw1HFMflZfPCGVxAEL6W/zxtAAPn7EjDTMIxh\n"
    "1hXIChiHAiorv19A/FL9kH9PHpEsAmWb0sIRm8VEKNZ2u8a2/2cHs2goPZlVk/jK\n"
    "ARe384okq1cU8PcA8DPVUjlqNJyzPbU7HtubcoObAqdixNdi+asaDJ4W5J8AKw/W\n"
    "cj4WjX8/AgMBAAECggEAFBtwyd6uS74KaHvmhDzTYzNKEA3I2uDb262RH3Qehvaw\n"
    "AdOV+tkg0Qnlz+efuCQsGYwOqpp80SATPJWqEXUyiFvmz0W3WTTGvQhqNmBcwpL0\n"
    "nXs5MTBATVqso6ISrtWphEEMnzt1whRNy8AUgzNXjwwjtCwCN6IMGgos152TVEis\n"
    "UkdonbDcxZ87nHSem9Oq+H0Kp9OOgoE6EoHaA3KWXAJzCC1hGBDa+0LTrYQrQPur\n"
    "pWPa7ugQMb0dGGNWzraBC3FP7G5S0/mIkQwd7zbXkheot8e5TZrAle865cnlP+R+\n"
    "D8hSZv2YEvIG4CLFjENRasbTvv4bM+HBbYgoAOLTUQKBgQDYgIav1TLS0YZ2nHyY\n"
    "Zdh578A5+PwPhO2uk3QD+CjKvwdEZ+92z49Cjit9VA93rKNPNPLoOyEjZdHzl6sz\n"
    "RRH/6CInMB5urgkAEfE2RkIO4abU3J30Nytu2mrqP+R6qx3Ok6gLLAE/CJdVZCNz\n"
    "k2weCVoIz1YVB5c3JjCuLHFAFwKBgQDSMduACtoJl0DuF9CB41RuZ7N3fdBt1K0k\n"
    "VWnSXOVZ2PFdXmgFQ3aPNIVVZx71Z4LXyi069Je9rNd2NdVgyC6uKVQDMmgPDTLA\n"
    "0rLYzJgkGbUEo7WjDHx7vpRCzS6iOp9DgaLfhA8wdF8ISyt3qqQLLgsBpziK8DjF\n"
    "EDSpmzTLGQKBgGO58FCWOC777KA+PPZGE403bqhFlHXhmUpNCae6a6/YhpRv+9IS\n"
    "kb7qlgXI7scFcsRNc4adlgokIK3AM1AOhNgIKZM7iwkYiXTKzv1dJ5iLQLnUVb3k\n"
    "m9EYMx9sBuaqY7SAN2vN/VT3tB3VXq8iPS8ox5w/RTuyn2j74niYaCJJAoGBAIfB\n"  # \C replaced with \n (line continuation in base64)
    "CaoV2CJvnNDpcpIhF4vC0Ccxi+cTf8vCmnjx5HL16VVLPtV/b9gnrKGu21DVzKy/\n"
    "+BxmkoY/Vl0Tgb9jKrrzGD6EVK678HaW3kmlQfG25LGdZhdrXg6x1KGcUS0XvXrl\n"
    "BCNl8EV0M1hw7B76h75su1ETBjK92Xx07f5Irn0pAoGBALP1oHSdBkpB9o/d/zaF\n"
    "zS82RAVQhbagI7+8FGhjJKpBxeU5T+ezJADdy+nIr4AUpSihYIqo9kgYFjI8f4cZ\n"
    "BAPAoxVhAoxsGGNOxD48Y2m6FU8l7d7yWWxL2ukdDWD3UZu+jUm2L+g9hLGvGOZu\n"
    "P6CI51bksQ9sqx0/HcknHHwb\n"
    "-----END PRIVATE KEY-----\n"
)

data = {
    "type": "service_account",
    "project_id": "educational-copilot",
    "private_key_id": "5f8bd2d7494c06cf1783d253fca4ef9574e3a382",
    "private_key": private_key,
    "client_email": "firebase-adminsdk-fbsvc@educational-copilot.iam.gserviceaccount.com",
    "client_id": "106961096247601002269",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40educational-copilot.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

out = pathlib.Path("d:/mini-project/Multi-Agent-Educational-Copilot/backend/firebase-key.json")
out.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("firebase-key.json written OK")

# Verify it parses back
loaded = json.loads(out.read_text(encoding="utf-8"))
assert loaded["type"] == "service_account"
print("JSON validation passed")
