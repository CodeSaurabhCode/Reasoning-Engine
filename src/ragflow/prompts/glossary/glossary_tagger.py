from typing import List, Tuple

from src.ragflow.prompts import BaseContentParser, CommunicationProtocol, MessageTemplate

glossary_tagging_template = MessageTemplate(
template = [
    (
        "system",
        "You are an expert document analysis assistant.Your task is to extract important glossary terms from the provided chunk document. Focus only on meaningful technical terms, concepts, and phrases that are critical to understanding the material."
    ),
    (
        "user",
        '''
Your task is to generate a Glossary terms from provided content which might be a keyword, domain name, Only identify terms that are directly defined or described in the context. Do not make assumptions or use outside knowledge.

Guidelines:
- Identify meaningful technical terms, key concepts, and phrases essential to understanding the document.
- For each term, provide:
  - Term: [Name of the Term]
  - Definition: [Clear, concise explanation based strictly on the document content.]
- Keep definitions between 1 to 3 sentences.
- Do NOT invent or add external information; only use what is present in the document.
- Ignore general commentary, promotional language, or unrelated information.
- If no terms are found, simply return empty string
- Format the output exactly as:

## Train Example:
    CCS: Carbon Capture and Storage, a process supported by LedaFlow to make cleaner energy more affordable.CO2 and Hydrogen Transport: LedaFlow can model the transport of these gases, which are important for carbon capture and hydrogen energy system.
    Flow Assurance: LedaFlow helps engineers predict and mitigate flow problems like slugging, hydrate formation, and wax deposition, ensuring reliable pipeline operations.
    Hydrates: Ice-like formations of water and gas molecules that can block pipelines, requiring careful management of temperature and pressure.
    K-Spice: Dynamic Process Simulator by Kongsberg Digital, integrated with LedaFlow for comprehensive simulations.
    KDI: Kongsberg Digital, the company that commercialized and further developed LedaFlow.
    LIFT: LedaFlow Improvements to Flow Technology, a program aimed at continuously improving LedaFlow through collaboration with major oil and gas companies.
    MEG, MeOH, EtOH: Chemical abbreviations for Monoethylene Glycol, Methanol, and Ethanol, respectively, which are used as hydrate inhibitors in LedaFlow simulations.
    Multiphase Flow: LedaFlow simulates the flow of multiple fluids (gas, oil, water) simultaneously, which is crucial for understanding complex flow scenarios.
    R&D: Research & Development
    SINTEF: Stiftelsen for Industriell og Teknisk Forskning (Foundation for Industrial and Technical Research), a Norwegian research organization involved in the development of LedaFlow.
    Slugging: The formation and propagation of large liquid slugs (or "hydrodynamic slugs") in pipelines, which can cause pressure surges and operational problems.
    Transient Simulation: LedaFlow is designed to model dynamic changes in flow conditions over time, unlike steady-state simulators.
    Wax Deposition: The buildup of solid wax on pipeline walls, leading to reduced flow capacity, which can be simulated and managed with LedaFlow.

## Input:
**Content Chunk**: '{content}'

## Output Format:
Return one glossary entry per line using the following format:
        '''.strip()),
],
        input_variables = ["content"]
)


class glossaryContentParser(BaseContentParser):
        def encode(self, content: str, **kwargs) -> Tuple[str,dict]:
                title = kwargs.get("title", None)
                if title is not None:
                        content = f"Title: {title}. Content: {content}"
                return content, {}
        
        def decode(self, content: str, **kwargs) -> List[str]:
                glossaries = content.split("\n")
                glossaries = [glossary.strip() for glossary in glossaries if len(glossary.strip()) > 0]
                return glossaries
        
glossary_tagging_protocol = CommunicationProtocol(
        template=glossary_tagging_template,
        parser = glossaryContentParser(),
)
              