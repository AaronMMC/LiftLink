import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers"))

from shared.db import (
    instructor_pk,
    instructor_sk,
    progress_pk,
    progress_sk,
    instructor_progress_pk,
    instructor_progress_sk,
    gsi1_pk,
    gsi1_sk,
)


class TestInstructorKeys:
    def test_instructor_pk(self):
        assert instructor_pk("user-123") == "INSTRUCTOR#user-123"

    def test_instructor_sk(self):
        assert instructor_sk() == "PROFILE"

    def test_instructor_pk_different_ids(self):
        assert instructor_pk("a") != instructor_pk("b")


class TestProgressKeys:
    def test_progress_pk(self):
        assert progress_pk("client-456") == "PROGRESS#client-456"

    def test_progress_sk(self):
        result = progress_sk("2026-07-25T10:00:00", "entry-789")
        assert result == "ENTRY#2026-07-25T10:00:00#entry-789"

    def test_instructor_progress_pk(self):
        assert instructor_progress_pk("inst-001") == "INSTRUCTOR_PROGRESS#inst-001"

    def test_instructor_progress_sk(self):
        result = instructor_progress_sk("2026-07-25T10:00:00", "entry-789")
        assert result == "ENTRY#2026-07-25T10:00:00#entry-789"


class TestGSI1Keys:
    def test_gsi1_pk(self):
        assert gsi1_pk("yoga") == "SPECIALTY#YOGA"

    def test_gsi1_sk(self):
        assert gsi1_sk("new york") == "LOCATION#NEW YORK"

    def test_gsi1_pk_case_insensitive(self):
        assert gsi1_pk("Yoga") == gsi1_pk("YOGA") == gsi1_pk("yoga")

    def test_gsi1_sk_case_insensitive(self):
        assert gsi1_sk("New York") == gsi1_sk("NEW YORK") == gsi1_sk("new york")
