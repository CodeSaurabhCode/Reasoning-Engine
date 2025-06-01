from typing import Dict, List, Tuple
from src.ragflow.prompts import CommunicationProtocol, BaseContentParser, MessageTemplate
from src.ragflow.utils.json_parser import parse_json, parse_json_v2

glossary_template = MessageTemplate(
        template = [
                (
                        "system",
                        "You are an AI language model designed to extract glossary terms and their definitions from provided text. A glossary term is typically a key word or phrase that is important to understand the context, subject, or domain of the text. Your task is to analyze the paragraph and identify any potential glossary terms, along with concise definitions based strictly on the content."
                ),
                (
                        "user",
                        """
                        Your task is to generate a Glossary terms which might be a keyword, domain name, Only identify terms that are directly defined or described in the context. Do not make assumptions or use outside knowledge. If no glossary entries are found, return an empty list.
                        ## Objective 
                        Glossary entries should be contexual,
                        Extract glossary terms and their definitions from the following text
                        
                        training Example:
                                CCS: Carbon Capture and Storage, a process supported by LedaFlow to make cleaner energy more affordable.
                                CO2 and Hydrogen Transport: LedaFlow can model the transport of these gases, which are important for carbon capture and hydrogen energy system.
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
                        like the above example having glossary you have generate response for:
                        ## Input:
                        ** Content topic**: '{content}'
                        ** User query / context**: '{query}'
                        ## Output format:
                        
                        the glossary entries contains bold keywords and normal sentance explainig them and each keyword will start from new line do not use the previous one.
                        
                        """.strip()
                ),
        ],
        input_variables=['content', 'query'],
)
class glossary_genParser(BaseContentParser):
        def encode(self, content: str,references: Dict[str,str]={}, **Kwargs)-> Tuple[str,dict]:
                return content,{
                        "query": references
                }
        
        def decode(self, content: str, **kwargs)-> Dict[str,str]:
                try:
                        output = parse_json(content)
                except Exception as e:
                        print(f'content:{content}, \n Exception as {e}')
                        try:
                                output = parse_json_v2(content)
                        except Exception as e2:
                                print(f'Exception arises as {e2}')
                                return {
                                        'parsing error'
                                }
                for key, value in output.item():
                        output[key] = str(value)
                        return output
                
glossary_generation_protocol = CommunicationProtocol(
        template= glossary_template,
        parser = glossary_genParser()
)

glossary_chat_template = MessageTemplate(
        template = [
                (
                        "system", "You are an AI language model designed to extract glossary terms and their definitions from provided text"
                ),
                (
                        "user", """ 
                        Your task is to generate a Glossary terms which might be a keyword, domain name, Only identify terms that are directly defined or described in the context. Do not make assumptions or use outside knowledge. If no glossary entries are found, return an empty list. and generate contextual glossary from provided content.
                        ## Objective 
                        Glossary entries should be contexual,
                        Extract glossary terms and their definitions from the following text
                        
                        training Example:
                                CCS: Carbon Capture and Storage, a process supported by LedaFlow to make cleaner energy more affordable.
                                CO2 and Hydrogen Transport: LedaFlow can model the transport of these gases, which are important for carbon capture and hydrogen energy system.
                                Flow Assurance: LedaFlow helps engineers predict and mitigate flow problems like slugging, hydrate formation, and wax deposition, ensuring reliable pipeline operations.
                                Hydrates: Ice-like formations of water and gas molecules that can block pipelines, requiring careful management of temperature and pressure.
                                K-Spice: Dynamic Process Simulator by Kongsberg Digital, integrated with LedaFlow for comprehensive simulations.
                                KDI: Kongsberg Digital, the company that commercialized and further developed LedaFlow.
                                LIFT: LedaFlow Improvements to Flow Technology, a program aimed at continuously improving LedaFlow through collaboration with major oil and gas companies.
                        like the above example having glossary you have generate response for:
                        ## Input:
                        ** Content topic**: '{content}'
                        ** User query / context**: '{query}'
                        ## Output format:
                        
                        the glossary entries contains bold keywords and normal sentance explainig them and each keyword will start from new line do not use the previous one.
                        """.strip()
                ),
        ],
        input_variables=["content", "query"],
)

class glossary_chat_parser(BaseContentParser):
        def encode(self, content: str,references: Dict[str,str]={}, **Kwargs) ->Tuple[str,dict]:
                return content,{
                        "query": references
                }
        def decode(self, content: str, **kwargs)->Dict[str,str]:
                try:
                        output = parse_json(content)
                except Exception as e:
                        print(f'content:{content}, \n Exception as {e}')
                        try:
                                output = parse_json_v2(content)
                        except Exception as e2:
                                print(f'Exception arises as {e2}')
                                return {
                                        'parsing error'
                                }
                for key, value in output.item():
                        output[key] = str(value)
                        return output
glossary_chat_protocol = CommunicationProtocol(
        template=glossary_chat_template,
        parser = glossary_chat_parser()
)