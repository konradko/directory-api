from enrolment import models


def test_trusted_source_signup_code_str():
    instance = models.PreVerifiedCompany(email_address='jim@example.com')

    assert str(instance) == 'jim@example.com'
