"""
Pydantic models for Internet Archive metadata.

Based on the Internet Archive Metadata Schema:
https://archive.org/developers/metadata-schema/index.html
"""

import re
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


class IAMetadata(BaseModel):
    """Internet Archive item metadata model.
    
    Only identifier and mediatype are required fields. All other fields are optional.
    """

    # Required fields (only identifier and mediatype are required by IA)
    identifier: Annotated[
        str,
        StringConstraints(
            min_length=5,
            max_length=100,
            pattern=r"^(@?[A-Za-z0-9][A-Za-z0-9._-]*)$",
        ),
    ] = Field(
        ...,
        description=(
            "Unique identifier for an item on archive.org. "
            "Must contain only Roman alphabet characters, numbers, periods (.), "
            "underscores (_), or dashes (-). First character must be alphanumeric, "
            "except for account items which begin with @ symbol."
        ),
    )
    mediatype: Literal[
        "texts",
        "etree",
        "audio",
        "movies",
        "software",
        "image",
        "data",
        "web",
        "collection",
        "account",
    ] = Field(..., description="Type of media content in the item")
    
    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """
        Validate identifier format according to IA requirements.
        
        Rules:
        - Length: 5-100 characters
        - Characters: Roman alphabet, numbers, periods (.), underscores (_), dashes (-)
        - First character: Must be alphanumeric (exception: @ for account items)
        """
        if len(v) < 5 or len(v) > 100:
            raise ValueError("Identifier must be between 5 and 100 characters")
        
        # Account identifiers can start with @
        if v.startswith("@"):
            # Check rest of identifier after @
            if len(v) < 6:  # @ + at least 5 chars
                raise ValueError(
                    "Account identifier must have at least 5 characters after @"
                )
            rest = v[1:]
            if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", rest):
                raise ValueError(
                    "Account identifier after @ must start with alphanumeric "
                    "and contain only letters, numbers, periods, underscores, or dashes"
                )
        else:
            # Regular identifiers must start with alphanumeric
            if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", v):
                raise ValueError(
                    "Identifier must start with alphanumeric character "
                    "and contain only letters, numbers, periods, underscores, or dashes"
                )
        
        return v
    
    # All other fields are optional
    addeddate: Optional[str] = Field(
        None, description="Date and time item was added to public search or created"
    )
    publicdate: Optional[str] = Field(
        None, description="Date and time item was created on archive.org"
    )

    # Descriptive metadata (recommended)
    title: Optional[str] = Field(None, description="Title of media")
    description: Optional[str] = Field(
        None, description="Description of the media content"
    )

    # Creator/Contributor information
    creator: Optional[List[str]] = Field(
        None, description="Individual(s) or organization that created the media content"
    )
    creator_alt_script: Optional[str] = Field(
        None, alias="creator-alt-script", description="Creator in alternate script"
    )
    contributor: Optional[str] = Field(
        None,
        description="Person or organization that provided the physical or digital media",
    )

    # Publication information
    date: Optional[str] = Field(
        None, description="Date of publication (YYYY, YYYY-MM, or YYYY-MM-DD)"
    )
    publisher: Optional[str] = Field(None, description="Publisher of the media")

    # Collections and classification
    collection: Optional[List[str]] = Field(
        None, description="Collection(s) this item belongs to"
    )
    subject: Optional[List[str]] = Field(
        None, description="Subjects and/or topics covered by the media content"
    )

    # Language and location
    language: Optional[List[str]] = Field(
        None, description="Language the media is written or recorded in"
    )
    coverage: Optional[List[str]] = Field(
        None, description="Geographic or subject area covered by item"
    )

    # Rights and licensing
    licenseurl: Optional[str] = Field(None, description="URL of the selected license")
    rights: Optional[str] = Field(None, description="Rights statement")
    possible_copyright_status: Optional[str] = Field(
        None,
        alias="possible-copyright-status",
        description="Information relevant to copyright status",
    )

    # Identifiers
    isbn: Optional[List[str]] = Field(None, description="ISBN-10 or ISBN-13")
    issn: Optional[List[str]] = Field(None, description="ISSN identifier")
    lccn: Optional[List[str]] = Field(
        None, description="Library of Congress Call Number"
    )
    oclc_id: Optional[List[str]] = Field(
        None, alias="oclc-id", description="OCLC identifier"
    )
    identifier_ark: Optional[str] = Field(
        None, alias="identifier-ark", description="Archival Resource Key identifier"
    )
    identifier_bib: Optional[List[str]] = Field(
        None, alias="identifier-bib", description="Additional local identifiers"
    )
    external_identifier: Optional[List[str]] = Field(
        None,
        alias="external-identifier",
        description="URLs or identifiers to outside resources",
    )

    # Open Library identifiers
    openlibrary: Optional[str] = Field(
        None, description="Deprecated. Open Library edition identifier"
    )
    openlibrary_edition: Optional[str] = Field(
        None,
        alias="openlibrary_edition",
        description="Open Library edition identifier (OL#M)",
    )
    openlibrary_work: Optional[str] = Field(
        None,
        alias="openlibrary_work",
        description="Open Library work identifier (OL#W)",
    )
    openlibrary_author: Optional[List[str]] = Field(
        None,
        alias="openlibrary_author",
        description="Open Library author identifier (OL#A)",
    )
    openlibrary_subject: Optional[List[str]] = Field(
        None, alias="openlibrary_subject", description="Open Library subject tags"
    )

    # Physical item metadata
    call_number: Optional[str] = Field(
        None,
        alias="call_number",
        description="Contributing library's local call number",
    )
    size: Optional[List[str]] = Field(
        None, description="Size of physical item digitized"
    )
    condition: Optional[
        Literal[
            "Mint",
            "Near Mint",
            "Very Good",
            "Good",
            "Fair",
            "Worn",
            "Poor",
            "Fragile",
            "Incomplete",
        ]
    ] = Field(None, description="Condition of media")
    condition_visual: Optional[
        Literal[
            "Mint",
            "Near Mint",
            "Very Good",
            "Good",
            "Fair",
            "Worn",
            "Poor",
            "Fragile",
            "Incomplete",
            "None",
            "Unknown",
        ]
    ] = Field(
        None,
        alias="condition-visual",
        description="Condition of artwork or printed materials",
    )

    # Scanning/digitization metadata
    scandate: Optional[str] = Field(
        None, description="Date and time the media was captured"
    )
    scanner: Optional[str] = Field(
        None, description="Machinery used to digitize or collect the media"
    )
    camera: Optional[str] = Field(
        None, description="Camera model used during digitization process"
    )
    ppi: Optional[int] = Field(None, description="Pixels per inch")
    source: Optional[str] = Field(None, description="Source of media")

    # Book/text specific fields
    volume: Optional[str] = Field(None, description="Volume number or name")
    bookreader_defaults: Optional[Literal["mode/1up", "mode/2up", "mode/thumb"]] = (
        Field(
            None,
            alias="bookreader-defaults",
            description="Bookreader display mode defaults",
        )
    )
    page_progression: Optional[Literal["lr", "rl"]] = Field(
        None,
        alias="page-progression",
        description="Direction pages will be turned (left-to-right or right-to-left)",
    )
    betterpdf: Optional[Literal["true"]] = Field(
        None, description="Create higher quality PDF derivative"
    )
    adaptive_ocr: Optional[Literal["true"]] = Field(
        None,
        alias="adaptive_ocr",
        description="Allow deriver to skip pages that would disrupt OCR",
    )
    bwocr: Optional[str] = Field(
        None, description="Page numbers or ranges to OCR as B&W"
    )
    fixed_ppi: Optional[int] = Field(
        None, alias="fixed-ppi", description="Change PPI to specific resolution"
    )

    # Audio/Video specific fields
    runtime: Optional[List[str]] = Field(
        None, description="Length of audio or video item (HH:MM:SS)"
    )
    aspect_ratio: Optional[str] = Field(
        None,
        alias="aspect_ratio",
        description="Ratio of pixel width and height of video stream",
    )
    frames_per_second: Optional[float] = Field(
        None,
        alias="frames_per_second",
        description="Frequency at which consecutive images are displayed",
    )
    audio_codec: Optional[str] = Field(
        None, alias="audio_codec", description="Program used to decode audio stream"
    )
    audio_sample_rate: Optional[int] = Field(
        None, alias="audio_sample_rate", description="Audio samples per second"
    )
    color: Optional[str] = Field(
        None, description="Indicates whether media is in color or black and white"
    )
    sound: Optional[Literal["sound", "silent"]] = Field(
        None, description="Indicates whether media has sound or is silent"
    )
    closed_captioning: Optional[Literal["yes", "no"]] = Field(
        None,
        alias="closed_captioning",
        description="Indicates whether item contains closed captioning files",
    )
    ccnum: Optional[str] = Field(
        None, description="Closed captioning file number to use"
    )

    # Web archive specific fields
    firstfiledate: Optional[str] = Field(
        None, description="Creation date of earliest file in item (YYYYMMDDHHMMSS)"
    )
    lastfiledate: Optional[str] = Field(
        None, description="Creation date of oldest file in item (YYYYMMDDHHMMSS)"
    )

    # Collection specific fields
    sort_by: Optional[
        Literal[
            "addeddate",
            "-addeddate",
            "creatorSorter",
            "-creatorSorter",
            "date",
            "-date",
            "downloads",
            "-downloads",
            "publicdate",
            "-publicdate",
            "reviewdate",
            "-reviewdate",
            "titleSorter",
            "-titleSorter",
        ]
    ] = Field(None, alias="sort-by", description="Default collection sort order")
    summary: Optional[str] = Field(
        None, description="Summary section for collection pages"
    )

    # Additional metadata
    notes: Optional[List[str]] = Field(
        None, description="Additional notes about the item"
    )
    title_alt_script: Optional[str] = Field(
        None, alias="title-alt-script", description="Title in alternate script"
    )

    # Deprecated fields
    year: Optional[str] = Field(
        None, deprecated=True, description="Deprecated. Use 'date' field instead"
    )

    # Internal/system fields (read-only)
    imagecount: Optional[int] = Field(
        None, description="Number of images/pages in item"
    )
    noindex: Optional[Literal["true"]] = Field(
        None, description="Prevents item from being indexed in public search"
    )
    hidden: Optional[Literal["true"]] = Field(
        None, description="Hides collection from top level navigation"
    )
    access_restricted: Optional[Literal["true"]] = Field(
        None,
        alias="access-restricted",
        description="Collection contents are restricted access",
    )
    access_restricted_item: Optional[Literal["true"]] = Field(
        None, alias="access-restricted-item", description="Item is access-restricted"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "identifier": "SanFrancisco1955CinemascopeFilm",
                "mediatype": "movies",
                "title": "San Francisco (1955 Cinemascope film)",
                "description": "Cinemascope homage to the city of San Francisco",
                "creator": ["Tullio Pellegrini"],
                "date": "1955",
                "language": ["eng"],
                "collection": ["opensource_movies"],
                "runtime": ["00:15:00"],
                "color": "color",
                "sound": "sound",
            }
        },
    )


class IAFileMetadata(BaseModel):
    """Metadata for individual files within an IA item."""

    name: str = Field(..., description="Filename")
    source: Optional[str] = Field(None, description="Source file type")
    format: Optional[str] = Field(None, description="File format")
    mtime: Optional[str] = Field(None, description="Last modified time")
    size: Optional[str] = Field(None, description="File size in bytes")
    md5: Optional[str] = Field(None, description="MD5 checksum")
    crc32: Optional[str] = Field(None, description="CRC32 checksum")
    sha1: Optional[str] = Field(None, description="SHA1 checksum")
    length: Optional[str] = Field(None, description="Length/duration for media files")
    height: Optional[str] = Field(None, description="Height in pixels for image/video")
    width: Optional[str] = Field(None, description="Width in pixels for image/video")
    track: Optional[str] = Field(None, description="Track number for audio files")
    title: Optional[str] = Field(None, description="Track title for audio files")
    album: Optional[str] = Field(None, description="Album name for audio files")
    artist: Optional[str] = Field(None, description="Artist name for audio files")
    creator: Optional[str] = Field(None, description="Creator of the file")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "example_file.mp4",
                "format": "h.264",
                "size": "12345678",
                "md5": "abc123def456",
                "mtime": "1234567890",
                "length": "1234.56",
            }
        }
    )


class IAItem(BaseModel):
    """Complete Internet Archive item with metadata and files."""

    metadata: IAMetadata = Field(..., description="Item metadata")
    files: Optional[List[IAFileMetadata]] = Field(
        None, description="List of files in the item"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "identifier": "example-item",
                    "mediatype": "texts",
                    "title": "Example Book",
                    "creator": ["Example Author"],
                },
                "files": [
                    {
                        "name": "example_file.pdf",
                        "format": "Text PDF",
                        "size": "1234567",
                    }
                ],
            }
        }
    )
