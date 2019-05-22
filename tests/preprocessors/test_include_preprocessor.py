import pytest
from hon.preprocessors.include import (
    _parse_include_arguments, _parse_target,
    find_includes,
    IncludeItem, IncludeRange, EscapedInclude, Playpen, SelectRange
)


def test__parse_include_arguments_without_extra_args():
    s = 'foo.md'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md', [])

    s = 'foo.md:1:2'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md:1:2', [])

    s = 'foo.md::'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md::', [])


def test__parse_include_arguments_with_extra_args():
    s = 'foo.md arg1'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md', ['arg1'])

    s = 'foo.md:: arg1'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md::', ['arg1'])

    s = 'foo.md:1:2 arg1'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md:1:2', ['arg1'])

    s = 'foo.md arg1 arg2'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md', ['arg1', 'arg2'])

    s = 'foo.md:: arg1 arg2'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md::', ['arg1', 'arg2'])

    s = 'foo.md:1:2 arg1 arg2'

    actual = _parse_include_arguments(s)
    assert actual == ('foo.md:1:2', ['arg1', 'arg2'])


def test__parse_target_with_range():
    s = 'foo.md:5'

    actual = _parse_target(s)
    assert actual == ('foo.md', SelectRange(start=5))

    s = 'foo.md:5:10'

    actual = _parse_target(s)
    assert actual == ('foo.md', SelectRange(start=5, stop=10))

    s = 'foo.md::10'

    actual = _parse_target(s)
    assert actual == ('foo.md', SelectRange(stop=10))


def test__parse_target_without_range():
    s = 'foo.md'

    actual = _parse_target(s)
    assert actual == ('foo.md', None)

    s = 'foo.md::'

    actual = _parse_target(s)
    assert actual == ('foo.md', None)


def test_find_includes_no_link():
    s = "Some random text without link..."

    actual = find_includes(s) 
    assert actual == []


def test_find_includes_partial_link():
    s = "Some random text with {{#playpen..."
    actual = find_includes(s)
    assert actual == []

    s = "Some random text with {{#include..."
    actual = find_includes(s)
    assert actual == []

    s = "Some random text with \\{{#include..."
    actual = find_includes(s)
    assert actual == []


def test_find_includes_empty_link():
    s = "Some random text with {{#playpen}} and {{#playpen   }} {{}} {{#}}..."
    actual = find_includes(s)
    assert actual == []


def test_find_includes_unknown_link_type():
    s = "Some random text with {{#playpenz ar.rs}} and {{#incn}} {{baz}} {{#bar}}..."
    actual = find_includes(s)
    assert actual == []


def test_find_includes_simple_link():
    s = "Some random text with {{#playpen file.py}} and {{#playpen test.rs }}..."

    actual = find_includes(s)
    # print("OUTPUT: {}".format(actual))

    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=42,
            include=Playpen('file.py'),
            include_text='{{#playpen file.py}}'
        ),
        IncludeItem(
            start_index=47,
            end_index=68,
            include=Playpen('test.rs'),
            include_text='{{#playpen test.rs }}'
        ),
    ]

def test_find_includes_with_range():
    s = "Some random text with {{#include file.py:10:20}}..."
    actual = find_includes(s)

    #print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=48,
            include=IncludeRange("file.py", select_range=SelectRange(start=10, stop=20)),
            include_text="{{#include file.py:10:20}}",
        )
    ]


def test_find_includes_with_line_number():
    s = "Some random text with {{#include file.py:10}}..."
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=45,
            include=IncludeRange("file.py", select_range=SelectRange(start=10)),
            include_text="{{#include file.py:10}}",
        )
    ]


def test_find_includes_with_from_range():
    s = "Some random text with {{#include file.py:10:}}..."
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=46,
            include=IncludeRange("file.py", select_range=SelectRange(start=10)),
            include_text="{{#include file.py:10:}}",
        )
    ]


def test_find_includes_with_to_range():
    s = "Some random text with {{#include file.py::20}}..."
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=46,
            include=IncludeRange("file.py", select_range=SelectRange(stop=20)),
            include_text="{{#include file.py::20}}",
        )
    ]


def test_find_includes_with_full_range():
    s = "Some random text with {{#include file.py::}}..."
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=44,
            include=IncludeRange("file.py"),
            include_text="{{#include file.py::}}",
        )
    ]


def test_find_includes_with_no_range_specified():
    s = "Some random text with {{#include file.py}}..."
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))
    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=42,
            include=IncludeRange("file.py"),
            include_text="{{#include file.py}}",
        )
    ]


def test_find_includes_escaped_link():
    s = "Some random text with escaped playpen \\{{#playpen file.py editable}} ..."
    print(s)
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))

    assert actual == [
        IncludeItem(
            start_index=38,
            end_index=68,
            include=EscapedInclude(),
            include_text="\\{{#playpen file.py editable}}",
        )
    ]


def test_find_includes_gitbook_style():
    s = "Some random text with escaped playpen {{% include 'file.py' }} ..."
    print(s)
    actual = find_includes(s)
    print("OUTPUT: {}".format(actual))

    assert actual == [
        IncludeItem(
            start_index=22,
            end_index=42,
            include=IncludeRange("file.py"),
            include_text="{{% include 'file.py' }}",
        )
    ]


# #[test]
# fn test_replace_all_escaped() {
#     let start = r"
#     Some text over here.
#     ```hbs
#     \{{#include file.py}} << an escaped link!
#     ```";
#     let end = r"
#     Some text over here.
#     ```hbs
#     {{#include file.py}} << an escaped link!
#     ```";
#     assert_eq!(replace_all(start, "", "", 0), end);
# }



# #[test]
# fn test_find_playpens_with_properties() {
#     let s = "Some random text with escaped playpen {{#playpen file.py editable }} and some \
#                 more\n text {{#playpen my.rs editable no_run should_panic}} ...";

#     let res = find_links(s).collect::<Vec<_>>();
#     println!("\nOUTPUT: {:?}\n", res);
#     assert_eq!(
#         res,
#         vec![
#             Link {
#                 start_index=38,
#                 end_index=68,
#                 include=Playpen("file.py", vec!["editable"]),
#                 include_text="{{#playpen file.py editable }}",
#             },
#             Link {
#                 start_index=89,
#                 end_index=136,
#                 include=Playpen(
#                     "my.rs"),#                     vec!["editable", "no_run", "should_panic"],
#                 ),
#                 include_text="{{#playpen my.rs editable no_run should_panic}}",
#             },
#         ]
#     );
# }

# #[test]
# fn test_find_all_link_types() {
#     let s = "Some random text with escaped playpen {{#include file.py}} and \\{{#contents are \
#                 insignifficant in escaped link}} some more\n text  {{#playpen my.rs editable \
#                 no_run should_panic}} ...";

#     let res = find_links(s).collect::<Vec<_>>();
#     println!("\nOUTPUT: {:?}\n", res);
#     assert_eq!(res.len(), 3);
#     assert_eq!(
#         res[0],
#         Link {
#             start_index=38,
#             end_index=58,
#             include=IncludeRangeFull("file.py", ..),
#             include_text="{{#include file.py}}",
#         }
#     );
#     assert_eq!(
#         res[1],
#         Link {
#             start_index=63,
#             end_index=112,
#             include=Escaped,
#             include_text="\\{{#contents are insignifficant in escaped link}}",
#         }
#     );
#     assert_eq!(
#         res[2],
#         Link {
#             start_index=130,
#             end_index=177,
#             include=Playpen(
#                 "my.rs"),#                 vec!["editable", "no_run", "should_panic"]
#             ),
#             include_text="{{#playpen my.rs editable no_run should_panic}}",
#         }
#     );
# }

# }
