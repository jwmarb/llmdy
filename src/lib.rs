use pyo3::prelude::*;
use regex::Regex;

const COMMENT_PATTERN: &str = r"<[ ]*!--.*?--[ ]*>";
const BASE64_IMG_PATTERN: &str = r#"<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>"#;

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
    fn clean_attrs(el: &mut visdom::types::BoxDynElement) -> () {
        let binding = el.get_attributes();
        let attrs: Vec<&str> = binding.iter().map(|(key, _)| key.as_str()).collect();

        attrs.iter().for_each(|&attr| match attr {
            "src" | "alt" => {}
            _ => el.remove_attribute(attr),
        });

        el.children().for_each(|_, el| {
            clean_attrs(el);
            true
        });
    }
    let mut html = html.to_string();

    let comment_re = Regex::new(COMMENT_PATTERN).unwrap();
    html = comment_re.replace_all(&html, "").to_string();

    if clean_base64 {
        html = replace_base64_images(&html, "#");
    }

    let root = visdom::Vis::load(html).unwrap();

    if clean_svg {
        root.find("svg").remove();
    }

    root.find("style,script,meta,link").remove();

    root.children("*").for_each(|_, el| {
        clean_attrs(el);
        true
    });

    root.html()
}

#[pymodule]
fn sanitizer(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(clean_html, m)?)?;
    m.add_function(wrap_pyfunction!(get_html, m)?)?;
    Ok(())
}
