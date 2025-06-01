from typing import Dict, List, Tuple

from src.ragflow.prompts import CommunicationProtocol, BaseContentParser, MessageTemplate
from src.ragflow.utils.json_parser import parse_json_v2, parse_json

web_copy_template = MessageTemplate(
template = [
    ("system", "You are an expert web copywriter specializing in crafting persuasive, SEO-optimized, and high-converting content tailored for digital platforms. Only use content strictly from the provided document JSON — no assumptions or fabricated content."),
    ("user", """
# Task
Your task is to generate compelling web copy for the given request.  

**Objective:**  
Craft an engaging, conversion-focused web copy from the provided raw text content. The goal is to captivate the audience, communicate the product's value clearly, and inspire action — even if the text is unstructured or incomplete.  

**Input:**  
You will receive a string of raw parsed text content. This content may include product descriptions, feature highlights, testimonials, or call-to-action hints — sometimes mixed within paragraphs or headings, subheaings and content related to web copy.  

** Example Input (Raw Text): hust train like this **  
Nova X Pro — next-gen smartphone built for performance, photography, and speed. Next-Level Performance, Unstoppable Style
Meet the Nova X Pro — built for speed, designed to impress. With a **Snapdragon processor**, **108MP camera**, and **5G connectivity**, you get power, precision, and style — all in one. The OLED display brings your content to life, while the **all-day battery** keeps you going.   
Features: Snapdragon processor, 108MP camera, 5G, all-day battery, OLED display.  
---
the JSON output :
- **Summary:** High-performance smartphone with focus on speed and camera.  
- **Keywords:** smartphone, fast, 5G, camera, battery, OLED.  
- **Use Case:** Content creation, gaming, fast downloads, all-day use.  

# Context provided by the product owner for crafting the web copy:
    {context_if_any}

# Generate web copy from above content. strictly use information from the content, dont skip any information.
you are provided with a json object which contain the keys as the headline, and purpose and the guidelines for the content.
and the values contains the content for the respective keys. use the purpose and guidelines to craft the web copy from po document.
# Output format
Your output must strictly follow this format, ensuring it's JSON-compliant and parsable in Python:

{{
    "META DESCRIPTION": "<A concise, compelling meta description, derived strictly from the document>",
    "PAGE TITLE": "<Product Name and application name>",
    "HERO - MODULE": {{
        "headline": "<A powerful, benefit-driven headline sourced from the document>",
        "subheadline": "<A compelling subheadline>".
        so here just give the output of hero module as headline in list and subheadline is also in the list.
    }},
    "PRODUCT_FEATURE": Your task is to extract **product feature introductions** and their **detailed descriptions** from the provided contentnand description should have context as well.

- **Headline**: Short, attention-grabbing statements that introduce each feature.  
- **Subheadline**: Detailed descriptions that explain the feature's purpose, functionality, or benefits. should at least contain 250 words of explaination in brand voice and language.

Return the result strictly as two separate lists:
- **headline**: A list of feature introductions  
- **subheadline**: A list of corresponding detailed descriptions,
    
    "APPLICATION AREAS": "<Extract specific, practical areas or industries where the product excels from the document and present them as a string of bullet points (•) with a new line>",
    "RELATED PRODUCTS - MODULE": "<A direct, compelling call-to-action prompting immediate engagement, based on the whole document present them as a string of bullet points (•) with a new line>",
    "TALK TO AN EXPERT CTA - MODULE": "<identify any name are mentioned or any detils about the expert person>",
    "TESTIMONIALS - MODULE": "<check if there no testimomnial details then return ( empty string )>",
    "KEYWORDS": "<SEO-relevant keywords and phrases derived identify those keywords>",
    "TARGET AUDIENCE": "<A detailed profile of the ideal target audience, including demographics and pain points, sourced from the document>"
}}
use instructions that are provided for the subsections 

# Fallback Handling
- If a tag is missing or named differently, infer the content from related sections or surrounding context — but still only use information present in the document.
- Ensure output remains structured and high-converting, even with incomplete data.

# Web Copy Request
{context_if_any}

# Instructions
{content}
Let's craft a high-impact web copy step by step.
""".strip()),
    ],
    input_variables=["content", "context_if_any"],
)

class WebCopyParser(BaseContentParser):
    def encode(self, content: str, references: Dict[str, str]={}, **kwargs) -> Tuple[str, dict]:
        # if len(references) > 0:
        #     context_if_any = "Related context, reports, or articles: "
        #     for context in list(set(references)):
        #         context_if_any += f"\n{context}\n"
        # else:
        #     context_if_any = ""

        return content, {
            "context_if_any": references
        }

    def decode(self, content: str, **kwargs) -> Dict[str, str]:
        try:
            output = parse_json(content)
        except Exception as e:
            print(f"[WebCopyParser] Content: {content}\nException: {e}")
            try:
                output = parse_json_v2(content)
            except Exception as e2:
                print(f"  [WebCopyParser] Exception: {e2}")
                return {
                    "meta_description": "parsing error",
                    "page_title": "parsing error",
                    "hero_module": {"headline": "parsing error", "subheadline": "parsing error"},
                    "product_features": "parsing error",
                    "application_areas": "parsing error",
                    "related_products": "parsing error",
                    "call_to_action": "parsing error",
                    "testimonials": "parsing error",
                    "keywords": "parsing error",
                    "target_audience": "parsing error"
                }
        for key, value in output.items():
            output[key] = str(value)
        return output

web_copy_protocol = CommunicationProtocol(
    template=web_copy_template,
    parser=WebCopyParser(),
)
