import requests

def superops_main(organization_id, tool, body):
    url = "https://sq1security.superops.ai/api/v1/assets"
    headers = {
        "Authorization": "Bearer api-eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI4ODcxNzU0MTYzNzgzODMxNTUyIiwicmFuZG9taXplciI6IlxmIe-_ve-_vWljZO-_vTDvv70ifQ.aBUh2EPn7nRJKVPedWgvmccjC2qJOk_s9w0-8KT6zih1eG6TN4zoPoHIcv0rzss3SkrGPiYJ6U1foZhQGwjXd4eSnPmlv6bxx56OEUk_4IMTTuHFjW-ICEWUoeClqLraCq8tTVmMLSsfUcnbIdff8yKTrHKCFd3Sw6gF684OCw98sruEeOFeXCzleu5nj0w8wWyvq5pWN8C1cS-je-7boib3ufHaTxqytKvWqxo_2FRdPB-PayuImxWiTCSW_UcE4kYHNr_q9RN80rx0CzTq8NzoLNIUlmDKE6tjZGYI28nZU58TjVSgYKCM5mTBaVSFxaRN1N-gP913C2XQKndarg"  # Use your actual API token or credentials
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        assets = response.json()  # Parse the JSON response
        print(assets)
    else:
        print(f"Failed to retrieve assets. Status code: {response.status_code}")