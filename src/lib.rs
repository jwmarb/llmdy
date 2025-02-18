use pyo3::prelude::*;
use regex::Regex;

const SCRIPT_PATTERN: &str = r"<[ ]*script.*?\/[ ]*script[ ]*>";
const STYLE_PATTERN: &str = r"<[ ]*style.*?\/[ ]*style[ ]*>";
const META_PATTERN: &str = r"<[ ]*meta.*?>";
const COMMENT_PATTERN: &str = r"<[ ]*!--.*?--[ ]*>";
const LINK_PATTERN: &str = r"<[ ]*link.*?>";
const BASE64_IMG_PATTERN: &str = r#"<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>"#;
const SVG_PATTERN: &str = r"(<svg[^>]*>)(.*?)(<\/svg>)";
const BODY_PATTERN: &str = r"<body[^>]*>(.*?)<\/body>";

fn replace_svg(html: &str, new_content: &str) -> String {
    let re = Regex::new(SVG_PATTERN).unwrap();
    re.replace_all(html, format!("$1{}$3", new_content))
        .to_string()
}

fn replace_base64_images(html: &str, new_image_src: &str) -> String {
    let re = Regex::new(BASE64_IMG_PATTERN).unwrap();
    re.replace_all(html, format!(r#"<img src="{}"/>"#, new_image_src))
        .to_string()
}

#[pyfunction]
#[pyo3(signature = (url = ""))]
fn get_html(url: &str) -> String {
    let response = reqwest::blocking::get(url);
    match response {
        Ok(result) => result.text().unwrap_or("".to_string()),
        Err(_) => "".to_string(),
    }
}

#[pyfunction]
#[pyo3(signature = (html = "", clean_svg = false, clean_base64 = false))]
fn clean_html(html: &str, clean_svg: bool, clean_base64: bool) -> String {
    let mut html = html.to_string();

    let script_re = Regex::new(SCRIPT_PATTERN).unwrap();
    html = script_re.replace_all(&html, "").to_string();

    let style_re = Regex::new(STYLE_PATTERN).unwrap();
    html = style_re.replace_all(&html, "").to_string();

    let meta_re = Regex::new(META_PATTERN).unwrap();
    html = meta_re.replace_all(&html, "").to_string();

    let comment_re = Regex::new(COMMENT_PATTERN).unwrap();
    html = comment_re.replace_all(&html, "").to_string();

    let link_re = Regex::new(LINK_PATTERN).unwrap();
    html = link_re.replace_all(&html, "").to_string();

    if clean_svg {
        html = replace_svg(&html, "this is a placeholder");
    }

    if clean_base64 {
        html = replace_base64_images(&html, "#");
    }

    html
}

#[pymodule]
fn sanitizer(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(clean_html, m)?)?;
    m.add_function(wrap_pyfunction!(get_html, m)?)?;
    Ok(())
}
