"""
Tests for Internet Archive metadata models.
"""

import pytest
from pydantic import ValidationError

from ia.models import IAMetadata


@pytest.mark.parametrize(
    "metadata_dict,should_validate,test_id",
    [
        # Valid cases - minimal required fields only
        (
            {
                "identifier": "example-book-123",
                "mediatype": "texts",
            },
            True,
            "valid-minimal-required-fields-only",
        ),
        (
            {
                "identifier": "test_item",
                "mediatype": "data",
            },
            True,
            "valid-minimal-data-item",
        ),
        # Valid cases - with optional fields
        (
            {
                "identifier": "example-book-123",
                "mediatype": "texts",
                "title": "Example Book",
                "description": "A test book",
            },
            True,
            "valid-basic-text-item",
        ),
        (
            {
                "identifier": "movie-1955-cinemascope",
                "mediatype": "movies",
                "title": "San Francisco (1955 Cinemascope film)",
                "creator": ["Tullio Pellegrini"],
                "date": "1955",
                "language": ["eng"],
                "collection": ["opensource_movies"],
                "runtime": ["00:15:00"],
                "color": "color",
                "sound": "sound",
            },
            True,
            "valid-movie-with-metadata",
        ),
        (
            {
                "identifier": "audio_recording.001",
                "mediatype": "audio",
                "title": "Test Audio Recording",
                "runtime": ["01:23:45"],
                "sound": "sound",
            },
            True,
            "valid-audio-with-underscores-and-period",
        ),
        (
            {
                "identifier": "web-archive-2020",
                "mediatype": "web",
                "title": "Web Archive Test",
                "firstfiledate": "20200101000000",
                "lastfiledate": "20201231235959",
            },
            True,
            "valid-web-archive",
        ),
        # Valid cases - account identifiers with @
        (
            {
                "identifier": "@user-account-123",
                "mediatype": "account",
                "title": "User Account",
            },
            True,
            "valid-account-identifier-with-at-symbol",
        ),
        (
            {
                "identifier": "@testuser",
                "mediatype": "account",
            },
            True,
            "valid-account-minimal",
        ),
        # Valid cases - various identifier formats
        (
            {
                "identifier": "item.with.periods",
                "mediatype": "texts",
            },
            True,
            "valid-identifier-with-periods",
        ),
        (
            {
                "identifier": "item_with_underscores",
                "mediatype": "texts",
            },
            True,
            "valid-identifier-with-underscores",
        ),
        (
            {
                "identifier": "item-with-dashes",
                "mediatype": "texts",
            },
            True,
            "valid-identifier-with-dashes",
        ),
        (
            {
                "identifier": "123numeric-start",
                "mediatype": "texts",
            },
            True,
            "valid-identifier-starting-with-number",
        ),
        # Invalid cases - identifier too short
        (
            {
                "identifier": "abc",  # Less than 5 characters
                "mediatype": "texts",
                "title": "Invalid Item",
            },
            False,
            "invalid-identifier-too-short",
        ),
        # Invalid cases - identifier too long
        (
            {
                "identifier": "a" * 101,  # More than 100 characters
                "mediatype": "texts",
                "title": "Invalid Item",
            },
            False,
            "invalid-identifier-too-long",
        ),
        # Invalid cases - missing required identifier
        (
            {
                "mediatype": "texts",
                "title": "No Identifier",
            },
            False,
            "invalid-missing-identifier",
        ),
        # Invalid cases - missing required mediatype
        (
            {
                "identifier": "has-identifier-123",
                "title": "No Mediatype",
            },
            False,
            "invalid-missing-mediatype",
        ),
        # Invalid cases - invalid mediatype value
        (
            {
                "identifier": "example-item-123",
                "mediatype": "invalid-type",  # Not in allowed literal values
                "title": "Invalid Mediatype",
            },
            False,
            "invalid-mediatype-value",
        ),
        # Invalid cases - invalid identifier characters
        (
            {
                "identifier": "item with spaces",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-with-spaces",
        ),
        (
            {
                "identifier": "item#with$special",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-special-characters",
        ),
        (
            {
                "identifier": "item/with/slashes",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-with-slashes",
        ),
        # Invalid cases - identifier starting with invalid character
        (
            {
                "identifier": "-starts-with-dash",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-starts-with-dash",
        ),
        (
            {
                "identifier": "_starts_with_underscore",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-starts-with-underscore",
        ),
        (
            {
                "identifier": ".starts.with.period",
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-starts-with-period",
        ),
        # Invalid cases - account identifier too short after @
        (
            {
                "identifier": "@usr",  # Only 3 chars after @
                "mediatype": "account",
            },
            False,
            "invalid-account-identifier-too-short",
        ),
        # Invalid cases - invalid characters that are not allowed
        (
            {
                "identifier": "test!item",  # Exclamation mark not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-exclamation-mark",
        ),
        (
            {
                "identifier": "test&item",  # Ampersand not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-ampersand",
        ),
        (
            {
                "identifier": "test%item",  # Percent sign not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-percent-sign",
        ),
        (
            {
                "identifier": "test[item]",  # Brackets not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-brackets",
        ),
        (
            {
                "identifier": "test+item",  # Plus sign not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-plus-sign",
        ),
        (
            {
                "identifier": "test=item",  # Equals sign not allowed
                "mediatype": "texts",
            },
            False,
            "invalid-identifier-equals-sign",
        ),
        # Invalid cases - invalid condition value
        (
            {
                "identifier": "example-item-456",
                "mediatype": "texts",
                "condition": "Terrible",  # Not in allowed literal values
            },
            False,
            "invalid-condition-value",
        ),
        # Invalid cases - invalid sound value
        (
            {
                "identifier": "audio-item-789",
                "mediatype": "audio",
                "sound": "maybe",  # Must be "sound" or "silent"
            },
            False,
            "invalid-sound-value",
        ),
        # Invalid cases - invalid page_progression
        (
            {
                "identifier": "book-item-101",
                "mediatype": "texts",
                "page-progression": "up-down",  # Must be "lr" or "rl"
            },
            False,
            "invalid-page-progression",
        ),
    ],
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_iametadata_validation(metadata_dict, should_validate, test_id):
    """
    Test IAMetadata model validation with various valid and invalid inputs.

    Args:
        metadata_dict: Dictionary containing metadata fields
        should_validate: Boolean indicating if the metadata should pass validation
        test_id: String identifier for the test case
    """
    if should_validate:
        # Should successfully create the model
        metadata = IAMetadata(**metadata_dict)
        assert metadata.identifier == metadata_dict["identifier"]
        assert metadata.mediatype == metadata_dict["mediatype"]
    else:
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            IAMetadata(**metadata_dict)
        assert exc_info.value.error_count() > 0


def test_iametadata_with_all_fields():
    """Test creating IAMetadata with many optional fields populated."""
    metadata = IAMetadata(
        identifier="comprehensive-test-item",
        mediatype="texts",
        title="Comprehensive Test Item",
        description="A test item with many fields populated",
        creator=["Author One", "Author Two"],
        date="2024-01-15",
        publisher="Test Publisher",
        collection=["test_collection", "opensource"],
        subject=["testing", "pydantic", "validation"],
        language=["eng", "spa"],
        licenseurl="https://creativecommons.org/licenses/by/4.0/",
        isbn=["978-0-123456-78-9"],
        notes=["First note", "Second note"],
        imagecount=250,
        ppi=300,
    )

    assert metadata.identifier == "comprehensive-test-item"
    assert metadata.creator and len(metadata.creator) == 2
    assert metadata.subject and len(metadata.subject) == 3
    assert metadata.ppi == 300


def test_iametadata_with_aliases():
    """Test that field aliases work correctly."""
    metadata = IAMetadata(
        identifier="alias-test-item",
        mediatype="texts",
        **{  # type: ignore
            "creator-alt-script": "作者名",
            "title-alt-script": "タイトル",
            "page-progression": "rl",
            "bookreader-defaults": "mode/2up",
        },
    )

    assert metadata.creator_alt_script == "作者名"
    assert metadata.title_alt_script == "タイトル"
    assert metadata.page_progression == "rl"
    assert metadata.bookreader_defaults == "mode/2up"


def test_iametadata_optional_fields_default_to_none():
    """Test that optional fields default to None when not provided."""
    metadata = IAMetadata(
        identifier="minimal-item-001",
        mediatype="data",
    )

    assert metadata.title is None
    assert metadata.description is None
    assert metadata.creator is None
    assert metadata.date is None


def test_only_identifier_and_mediatype_required():
    """
    Test that identifier and mediatype are the ONLY required fields.
    All other fields should be optional and creation should succeed with just these two.
    """
    # Should succeed with just identifier and mediatype
    metadata = IAMetadata(
        identifier="test-item-12345",
        mediatype="texts",
    )

    assert metadata.identifier == "test-item-12345"
    assert metadata.mediatype == "texts"

    # Verify all other fields are None (optional)
    assert metadata.title is None
    assert metadata.description is None
    assert metadata.creator is None
    assert metadata.date is None
    assert metadata.publisher is None
    assert metadata.collection is None
    assert metadata.subject is None
    assert metadata.language is None
    assert metadata.addeddate is None
    assert metadata.publicdate is None


def test_account_identifier_validation():
    """Test that account identifiers with @ symbol are validated correctly."""
    # Valid account identifier
    metadata = IAMetadata(
        identifier="@testuser",
        mediatype="account",
    )
    assert metadata.identifier == "@testuser"

    # Valid account identifier with dashes and underscores
    metadata = IAMetadata(
        identifier="@test-user_123",
        mediatype="account",
    )
    assert metadata.identifier == "@test-user_123"

    # Invalid - account identifier too short after @
    with pytest.raises(ValidationError) as exc_info:
        IAMetadata(
            identifier="@usr",  # Only 3 chars after @
            mediatype="account",
        )
    assert exc_info.value.error_count() > 0


def test_identifier_format_validation():
    """Test various identifier format validations."""
    # Valid identifiers with different formats
    valid_identifiers = [
        "abc123",
        "123abc",
        "test-item",
        "test_item",
        "test.item",
        "Test-Item_123.xyz",
        "12345",
        "abcde",
    ]

    for identifier in valid_identifiers:
        metadata = IAMetadata(identifier=identifier, mediatype="texts")
        assert metadata.identifier == identifier

    # Invalid identifiers
    invalid_identifiers = [
        "-starts-with-dash",
        "_starts_with_underscore",
        ".starts.with.period",
        "has spaces",
        "has#special$chars",
        "has/slashes",
        "has@symbol",  # @ not allowed except at start for account items
    ]

    for identifier in invalid_identifiers:
        with pytest.raises(ValidationError):
            IAMetadata(identifier=identifier, mediatype="texts")


def test_repeatable_fields_accept_string_or_list():
    """
    Test that repeatable fields accept both string and list values.

    Per IA documentation, repeatable fields can be either:
    - str (single value)
    - List[str] (multiple values)
    - None (not set)

    The model should preserve the type as-is, not normalize.
    """
    # Test single string values are preserved as strings
    metadata = IAMetadata(
        identifier="test-string-values",
        mediatype="texts",
        collection="ol_data",  # String
        creator="Single Author",  # String
        subject="topic",  # String
        language="eng",  # String
        isbn="978-0-123456-78-9",  # String
    )

    assert metadata.collection == "ol_data"
    assert isinstance(metadata.collection, str)
    assert metadata.creator == "Single Author"
    assert isinstance(metadata.creator, str)
    assert metadata.subject == "topic"
    assert isinstance(metadata.subject, str)
    assert metadata.language == "eng"
    assert isinstance(metadata.language, str)
    assert metadata.isbn == "978-0-123456-78-9"
    assert isinstance(metadata.isbn, str)

    # Test that lists are preserved as lists
    metadata2 = IAMetadata(
        identifier="test-list-values",
        mediatype="texts",
        collection=["california-archive-citizen", "government-documents"],
        creator=["Author One", "Author Two"],
        subject=["topic1", "topic2"],
        language=["eng", "spa"],
    )

    assert metadata2.collection == [
        "california-archive-citizen",
        "government-documents",
    ]
    assert isinstance(metadata2.collection, list)
    assert metadata2.creator == ["Author One", "Author Two"]
    assert isinstance(metadata2.creator, list)
    assert metadata2.subject == ["topic1", "topic2"]
    assert isinstance(metadata2.subject, list)
    assert metadata2.language == ["eng", "spa"]
    assert isinstance(metadata2.language, list)

    # Test that None remains None
    metadata3 = IAMetadata(
        identifier="test-none-values",
        mediatype="texts",
    )

    assert metadata3.collection is None
    assert metadata3.creator is None
    assert metadata3.subject is None


def test_all_repeatable_fields_accept_both_types():
    """Test that all repeatable fields can accept strings OR lists."""
    # Test with string values
    string_fields = {
        "collection": "test-collection",
        "creator": "Test Creator",
        "subject": "test-subject",
        "language": "eng",
        "coverage": "test-coverage",
        "isbn": "123-456",
        "issn": "1234-5678",
        "lccn": "12345678",
        "oclc-id": "123456",
        "identifier-bib": "bib123",
        "external-identifier": "ext123",
        "openlibrary_author": "OL123A",
        "openlibrary_subject": "subject",
        "size": "8x10",
        "runtime": "01:30:00",
        "notes": "Test note",
    }

    metadata = IAMetadata(
        identifier="test-all-strings",
        mediatype="texts",
        **string_fields,  # type: ignore
    )

    # All should be preserved as strings
    assert metadata.collection == "test-collection"
    assert isinstance(metadata.collection, str)
    assert metadata.creator == "Test Creator"
    assert isinstance(metadata.creator, str)
    assert metadata.subject == "test-subject"
    assert isinstance(metadata.subject, str)

    # Test with list values
    list_fields = {
        "collection": ["col1", "col2"],
        "creator": ["Author1", "Author2"],
        "subject": ["subj1", "subj2"],
        "language": ["eng", "spa"],
        "isbn": ["123", "456"],
    }

    metadata2 = IAMetadata(
        identifier="test-all-lists",
        mediatype="texts",
        **list_fields,  # type: ignore
    )

    # All should be preserved as lists
    assert metadata2.collection == ["col1", "col2"]
    assert isinstance(metadata2.collection, list)
    assert metadata2.creator == ["Author1", "Author2"]
    assert isinstance(metadata2.creator, list)
