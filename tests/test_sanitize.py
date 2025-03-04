import pytest
import llmdy

_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
  </head>
  <body>
    <h1>Tutorial</h1>
    <p>This is how to make hello world in C</p>
    <pre><code>
      #define &lt;stdio.h&gt;

      int main() {
        fprintf(stdout, "Hello World!");
        return 0;
      }

    </code></pre>

    <h3>In Rust We Trust</h3>

    In Rust, it's a little different:

    <pre><code>
      fn main() -> () {
        println!("Hello World!");
      }
    </code></pre>
  </body>
</html>"""


def test_sanitize_md_removes_useless_tags():
    result = llmdy.sanitize.clean_html(_html, "_mock.html")

    with pytest.raises(ValueError) as excinfo:
        result.index('meta')

    assert str(excinfo.value) == "substring not found"


def test_sanitize_md_removes_useless_attributes():
    result = llmdy.sanitize.clean_html(
        "<html><body><h1 class=\"hello\" style=\"color: white\">Hi</h1></body></html>", "")

    assert result == "<body><h1>Hi</h1></body>"


def test_sanitize_md_resolve_src():

    # Absolute path
    result = llmdy.sanitize.clean_html(
        "<html><body><img src=\"/rel.png\"></body></html>", "https://example.com")

    assert result == "<body><img src=\"https://example.com/rel.png\"/></body>"

    # Should not affect src
    result = llmdy.sanitize.clean_html(
        "<html><body><img src=\"https://example.com/rel.png\"></body></html>", "https://example.com")

    assert result == "<body><img src=\"https://example.com/rel.png\"/></body>"

    # This one is a relative
    result = llmdy.sanitize.clean_html(
        "<html><body><img src=\"rel.png\"></body></html>", "https://example.com")

    assert result == "<body><img src=\"https://example.com/rel.png\"/></body>"

    # This one is a srcset instead
    result = llmdy.sanitize.clean_html(
        "<html><body><img srcset=\"rel.png\"></body></html>", "https://example.com")

    assert result == "<body><img srcset=\"https://example.com/rel.png\"/></body>"


def test_sanitize_md_handles_empty_html():
    result = llmdy.sanitize.clean_html("", "")
    assert result == ""


def test_sanitize_md_handles_script_tag():
    result = llmdy.sanitize.clean_html(
        "<html><body><script>alert('Hello');</script><p>Safe text</p></body></html>", "")
    assert result == "<body><p>Safe text</p></body>"


def test_sanitize_md_handles_style_tag():
    result = llmdy.sanitize.clean_html(
        "<html><body><style>body {color: black;}</style><p>Text</p></body></html>", "")
    assert result == "<body><p>Text</p></body>"


def test_sanitize_md_removes_comments():
    result = llmdy.sanitize.clean_html(
        "<html><body><!-- This is a comment --><p>Text</p></body></html>", ""
    )
    assert result == "<body><p>Text</p></body>"


def test_sanitize_md_removes_links_without_href():
    result = llmdy.sanitize.clean_html(
        "<html><body><a>This is a link</a></body></html>", ""
    )
    assert result == "<body><a>This is a link</a></body>"


# def test_sanitize_md_resolves_links_with_href():
#     result = llmdy.sanitize.clean_html(
#         "<html><body><a href=\"/relative\">Link</a></body></html>", "https://example.com"
#     )
#     assert result == "<body><a href=\"https://example.com/relative\">Link</a></body>"


# def test_sanitize_md_resolves_links_with_absolute_href():
#     result = llmdy.sanitize.clean_html(
#         "<html><body><a href=\"https://external.com\">Link</a></body></html>", "https://example.com"
#     )
#     assert result == "<body><a href=\"https://external.com\">Link</a></body>"


def test_sanitize_md_preserves_safe_tags():
    result = llmdy.sanitize.clean_html(
        "<html><body><p>Safe <em>text</em> with <strong>tags</strong>.</p></body></html>", ""
    )
    assert result == "<body><p>Safe <em>text</em> with <strong>tags</strong>.</p></body>"


def test_sanitize_md_removes_unsafe_attributes():
    result = llmdy.sanitize.clean_html(
        "<html><body><div style=\"color: red;\" onclick=\"alert('Attack!\');\">Unsafe</div></body></html>", ""
    )
    assert result == "<body><div>Unsafe</div></body>"


def test_remove_md_block_response_with_complete_block():
    generated = """```markdown
<!DOCTYPE html>
<html><body><h1>Hello World</h1></body></html>
```"""
    assert llmdy.sanitize.remove_md_block_response(
        generated) == "<!DOCTYPE html>\n<html><body><h1>Hello World</h1></body></html>"


def test_remove_md_block_response_with_leading_and_trailing_blocks():
    generated = """```markdown
    Hello
    ```js
    console.log('hi');
    ``` again
    ```python
    print("Hi")
    ```
    ```"""

    assert llmdy.sanitize.remove_md_block_response(generated) == """Hello
    ```js
    console.log('hi');
    ``` again
    ```python
    print("Hi")
    ```"""
