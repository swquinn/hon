import pytest
from hon.preprocessors.index import is_readme


def test_is_readme_succeeds_for_readme_file_name_variations():
    assert is_readme('README.md') is True
    assert is_readme('readme.md') is True
    assert is_readme('ReadMe.md') is True

    #: Test alternative extensions, these should all return true as well, since
    #: we're not checking the extension, only the file name.
    assert is_readme('README.rst') is True
    assert is_readme('README') is True


def test_is_readme_returns_false_for_non_readme_file_names():
    assert is_readme('REDME.md') is False
    assert is_readme('RADME.md') is False
    assert is_readme('READEM.md') is False

# #[cfg(test)]
# mod tests {
#     use super::*;

#     #[test]
#     fn file_stem_exactly_matches_readme_case_insensitively() {
#         let path = "path/to/Readme.md";
#         assert!(is_readme_file(path));

#         let path = "path/to/README.md";
#         assert!(is_readme_file(path));

#         let path = "path/to/rEaDmE.md";
#         assert!(is_readme_file(path));

#         let path = "path/to/README.markdown";
#         assert!(is_readme_file(path));

#         let path = "path/to/README";
#         assert!(is_readme_file(path));

#         let path = "path/to/README-README.md";
#         assert!(!is_readme_file(path));
#     }
# }
