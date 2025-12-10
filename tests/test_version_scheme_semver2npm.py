import pytest

from commitizen.version_schemes import SemVer2Npm, VersionProtocol


class TestSemVer2NpmBuildMetadata:
    """Test that SemVer2Npm uses hyphen instead of plus for build metadata."""

    @pytest.mark.parametrize(
        "version, increment, build_metadata, expected",
        [
            # Basic build metadata cases
            ("1.0.0", "PATCH", "abc123", "1.0.1-abc123"),
            ("1.0.0", "MINOR", "abc123", "1.1.0-abc123"),
            ("1.0.0", "MAJOR", "abc123", "2.0.0-abc123"),
            # Long git hash as build metadata (the main use case)
            (
                "1.16.0",
                "PATCH",
                "dab80a86fea3165b51c2e2d09ecc9b1d8470653a",
                "1.16.1-dab80a86fea3165b51c2e2d09ecc9b1d8470653a",
            ),
            # No build metadata (should behave same as SemVer2)
            ("1.0.0", "PATCH", None, "1.0.1"),
        ],
    )
    def test_build_metadata_uses_hyphen(
        self, version, increment, build_metadata, expected
    ):
        result = SemVer2Npm(version).bump(
            increment=increment,
            build_metadata=build_metadata,
        )
        assert str(result) == expected

    @pytest.mark.parametrize(
        "version, increment, prerelease, devrelease, build_metadata, expected",
        [
            # Dev release with build metadata
            ("1.0.0", "PATCH", None, 1, "abc123", "1.0.1-dev.1-abc123"),
            # Prerelease with build metadata
            ("1.0.0", "PATCH", "alpha", None, "abc123", "1.0.1-alpha.0-abc123"),
            # Dev release with prerelease and build metadata
            ("1.0.0", "PATCH", "alpha", 1, "abc123", "1.0.1-alpha.0.dev.1-abc123"),
            # Real world case: dev release with git hash
            (
                "1.15.0",
                "MINOR",
                None,
                23,
                "dab80a86fea3165b51c2e2d09ecc9b1d8470653a",
                "1.16.0-dev.23-dab80a86fea3165b51c2e2d09ecc9b1d8470653a",
            ),
        ],
    )
    def test_combined_prerelease_dev_and_build_metadata(
        self, version, increment, prerelease, devrelease, build_metadata, expected
    ):
        result = SemVer2Npm(version).bump(
            increment=increment,
            prerelease=prerelease,
            devrelease=devrelease,
            build_metadata=build_metadata,
        )
        assert str(result) == expected


class TestSemVer2NpmBehavesLikeSemVer2:
    """Test that SemVer2Npm behaves identically to SemVer2 when no build metadata is used."""

    @pytest.mark.parametrize(
        "version, increment, prerelease, devrelease, expected",
        [
            # Basic version bumps
            ("0.1.0", "PATCH", None, None, "0.1.1"),
            ("0.1.0", "MINOR", None, None, "0.2.0"),
            ("0.1.0", "MAJOR", None, None, "1.0.0"),
            # Dev releases
            ("0.1.0", "PATCH", None, 1, "0.1.1-dev.1"),
            ("0.2.0", "MINOR", None, 1, "0.3.0-dev.1"),
            # Prereleases
            ("0.3.0", "PATCH", "alpha", None, "0.3.1-alpha.0"),
            ("0.3.1-alpha.0", None, "alpha", None, "0.3.1-alpha.1"),
            # Combined prerelease and dev
            ("1.0.0-alpha.1", None, "alpha", 1, "1.0.0-alpha.2.dev.1"),
            # Prerelease transitions
            ("1.0.0-alpha.1", None, "beta", None, "1.0.0-beta.0"),
            ("1.0.0-beta.1", None, "rc", None, "1.0.0-rc.0"),
        ],
    )
    def test_standard_version_bumping(
        self, version, increment, prerelease, devrelease, expected
    ):
        result = SemVer2Npm(version).bump(
            increment=increment,
            prerelease=prerelease,
            devrelease=devrelease,
        )
        assert str(result) == expected


class TestSemVer2NpmPostRelease:
    """Test postrelease support in SemVer2Npm."""

    @pytest.mark.parametrize(
        "version, increment, postrelease, expected",
        [
            # Basic postrelease
            ("1.0.0", "PATCH", True, "1.0.1-post.0"),
            ("1.0.1-post.0", None, True, "1.0.1-post.1"),
            ("1.0.1-post.1", None, True, "1.0.1-post.2"),
        ],
    )
    def test_postrelease_bumping(self, version, increment, postrelease, expected):
        result = SemVer2Npm(version).bump(
            increment=increment,
            postrelease=postrelease,
        )
        assert str(result) == expected

    @pytest.mark.parametrize(
        "version, increment, postrelease, build_metadata, expected",
        [
            # Postrelease with build metadata
            ("1.0.0", "PATCH", True, "abc123", "1.0.1-post.0-abc123"),
            ("1.0.1-post.0", None, True, "def456", "1.0.1-post.1-def456"),
        ],
    )
    def test_postrelease_with_build_metadata(
        self, version, increment, postrelease, build_metadata, expected
    ):
        result = SemVer2Npm(version).bump(
            increment=increment,
            postrelease=postrelease,
            build_metadata=build_metadata,
        )
        assert str(result) == expected

    @pytest.mark.parametrize(
        "version, increment, prerelease, postrelease, devrelease, build_metadata, expected",
        [
            # All combined: prerelease + postrelease + devrelease + build metadata
            (
                "1.0.0",
                "PATCH",
                "alpha",
                True,
                1,
                "abc123",
                "1.0.1-alpha.0.post.0.dev.1-abc123",
            ),
        ],
    )
    def test_all_combined(
        self,
        version,
        increment,
        prerelease,
        postrelease,
        devrelease,
        build_metadata,
        expected,
    ):
        result = SemVer2Npm(version).bump(
            increment=increment,
            prerelease=prerelease,
            postrelease=postrelease,
            devrelease=devrelease,
            build_metadata=build_metadata,
        )
        assert str(result) == expected


class TestSemVer2NpmProtocol:
    """Test that SemVer2Npm implements the VersionProtocol."""

    def test_scheme_property(self):
        version = SemVer2Npm("0.0.1")
        assert version.scheme is SemVer2Npm

    def test_implements_version_protocol(self):
        assert isinstance(SemVer2Npm("0.0.1"), VersionProtocol)


class TestSemVer2NpmVsSemVer2:
    """Compare SemVer2Npm vs SemVer2 output with build metadata."""

    def test_difference_with_build_metadata(self):
        from commitizen.version_schemes import SemVer2

        # SemVer2 uses + for build metadata
        semver2_result = SemVer2("1.0.0").bump(
            increment="PATCH",
            build_metadata="abc123",
        )
        assert str(semver2_result) == "1.0.1+abc123"

        # SemVer2Npm uses - for build metadata
        semver2npm_result = SemVer2Npm("1.0.0").bump(
            increment="PATCH",
            build_metadata="abc123",
        )
        assert str(semver2npm_result) == "1.0.1-abc123"

    def test_no_difference_without_build_metadata(self):
        from commitizen.version_schemes import SemVer2

        # Both should produce identical output when no build metadata
        semver2_result = SemVer2("1.0.0").bump(
            increment="PATCH",
            devrelease=1,
        )
        semver2npm_result = SemVer2Npm("1.0.0").bump(
            increment="PATCH",
            devrelease=1,
        )
        assert str(semver2_result) == str(semver2npm_result) == "1.0.1-dev.1"
