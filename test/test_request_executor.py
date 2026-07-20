import unittest

from src.request_executor import redact_sensitive_headers


class RedactSensitiveHeadersTests(unittest.TestCase):
    def test_redacts_credentials_case_insensitively(self):
        headers = {
            "Authorization": "Bearer secret",
            "X-API-Key": "xq_secret",
            "Cookie": "session=secret",
            "Accept": "application/json",
        }

        self.assertEqual(
            redact_sensitive_headers(headers),
            {
                "Authorization": "[REDACTED]",
                "X-API-Key": "[REDACTED]",
                "Cookie": "[REDACTED]",
                "Accept": "application/json",
            },
        )

    def test_does_not_mutate_input(self):
        headers = {"x-api-key": "xq_secret"}

        redact_sensitive_headers(headers)

        self.assertEqual(headers, {"x-api-key": "xq_secret"})


if __name__ == "__main__":
    unittest.main()
