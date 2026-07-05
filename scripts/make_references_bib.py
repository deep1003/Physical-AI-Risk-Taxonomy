#!/usr/bin/env python3
"""Build Zotero-importable bibliography files (BibTeX .bib and RIS .ris) for every
reference cited in the Physical AI Risk Taxonomy Technical Report."""
import os
OUT = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex"

# (key, type, {fields})  type in: article, inproceedings, book, techreport, misc
E = [
 ("clarivate-wos","misc",dict(author="Clarivate",title="Web of Science Platform",year="2026",howpublished="Online",url="https://clarivate.com/academia-government/scientific-and-academic-research/research-discovery-and-referencing/web-of-science/")),
 ("openalex","misc",dict(author="{OpenAlex}",title="OpenAlex Developers: Overview",year="2026",howpublished="Online",url="https://developers.openalex.org/")),
 ("crossref-rest","misc",dict(author="{Crossref}",title="REST API: Retrieve Metadata",year="2026",howpublished="Online",url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/")),
 ("ror","misc",dict(author="{Research Organization Registry}",title="Research Organization Registry (ROR)",year="2026",howpublished="Online",url="https://ror.org/")),
 ("epo-patstat","misc",dict(author="{European Patent Office}",title="PATSTAT: EPO Worldwide Patent Statistical Database",year="2026",howpublished="Online",url="https://www.epo.org/en/service-support/faq/searching-patents/about-patent-information/where-can-i-find-patent-statistics")),
 ("kipris","misc",dict(author="{Korea Institute of Patent Information}",title="KIPRIS Intellectual Property Information Search Service",year="2026",howpublished="Online",url="https://www.kipris.or.kr/khome/main.do")),
 ("zupic2015","article",dict(author="Zupic, Ivan and {\\v{C}}ater, Toma{\\v{z}}",title="Bibliometric Methods in Management and Organization",journal="Organizational Research Methods",volume="18",number="3",pages="429--472",year="2015",doi="10.1177/1094428114562629")),
 ("vaneck2010","article",dict(author="van Eck, Nees Jan and Waltman, Ludo",title="Software survey: VOSviewer, a computer program for bibliometric mapping",journal="Scientometrics",volume="84",pages="523--538",year="2010",doi="10.1007/s11192-009-0146-3")),
 ("aria2017","article",dict(author="Aria, Massimo and Cuccurullo, Corrado",title="bibliometrix: An R-tool for comprehensive science mapping analysis",journal="Journal of Informetrics",volume="11",number="4",pages="959--975",year="2017",doi="10.1016/j.joi.2017.08.007")),
 ("hicks2015","article",dict(author="Hicks, Diana and Wouters, Paul and Waltman, Ludo and de Rijcke, Sarah and Rafols, Ismael",title="Bibliometrics: The Leiden Manifesto for research metrics",journal="Nature",volume="520",pages="429--431",year="2015",doi="10.1038/520429a")),
 ("oecd2009patent","techreport",dict(author="{OECD}",title="OECD Patent Statistics Manual",institution="OECD Publishing",year="2009",url="https://www.oecd.org/en/publications/2009/02/oecd-patent-statistics-manual_g1gh9fa4.html")),
 ("oecd-ipstats","misc",dict(author="{OECD}",title="Intellectual Property Statistics",year="2026",howpublished="Online",url="https://www.oecd.org/en/data/datasets/intellectual-property-statistics.html")),
 ("aacods","techreport",dict(author="Tyndall, Jess",title="AACODS Checklist for Appraising Grey Literature",institution="Flinders University",year="2010",url="https://fac.flinders.edu.au/dspace/api/core/bitstreams/e94a96eb-0334-4300-8880-c836d4d9a676/content")),
 ("tricco2018","article",dict(author="Tricco, Andrea C. and Lillie, Erin and Zarin, Wasifa and O'Brien, Kelly K. and Colquhoun, Heather and Levac, Danielle and Moher, David and Peters, Micah D. J. and Horsley, Tanya and Weeks, Laura and Hempel, Susanne and others",title="PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and Explanation",journal="Annals of Internal Medicine",volume="169",number="7",pages="467--473",year="2018",doi="10.7326/M18-0850")),
 ("nvidia-cosmos","misc",dict(author="{NVIDIA}",title="NVIDIA Cosmos: Physical AI with World Foundation Models",year="2026",howpublished="Online",url="https://www.nvidia.com/en-us/ai/cosmos/")),
 ("nist-airmf","techreport",dict(author="{National Institute of Standards and Technology}",title="Artificial Intelligence Risk Management Framework (AI RMF 1.0)",institution="NIST",year="2023",url="https://www.nist.gov/itl/ai-risk-management-framework")),
 ("iso23894","techreport",dict(author="{ISO/IEC}",title="ISO/IEC 23894:2023, Artificial intelligence --- Guidance on risk management",institution="ISO/IEC",year="2023",url="https://www.iso.org/standard/77304.html")),
 ("iso10218","techreport",dict(author="{ISO}",title="ISO 10218-1:2025, Robotics --- Safety requirements --- Part 1: Industrial robots",institution="ISO",year="2025",url="https://www.iso.org/standard/73933.html")),
 ("iso5469","techreport",dict(author="{ISO/IEC}",title="ISO/IEC TR 5469:2024, Artificial intelligence --- Functional safety and AI systems",institution="ISO/IEC",year="2024",url="https://www.iso.org/standard/81283.html")),
 ("iso8200","techreport",dict(author="{ISO/IEC}",title="ISO/IEC TS 8200:2024, Information technology --- Artificial intelligence --- Controllability of automated artificial intelligence systems",institution="ISO/IEC",year="2024",url="https://www.iso.org/standard/83012.html")),
 ("mitre-atlas","misc",dict(author="{MITRE}",title="ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems",year="2026",howpublished="Online",url="https://atlas.mitre.org/")),
 ("sermanet-asimov","article",dict(author="Sermanet, Pierre and Majumdar, Anirudha and Irpan, Alex and Kalashnikov, Dmitry and Sindhwani, Vikas",title="Generating Robot Constitutions and Benchmarks for Semantic Safety",journal="arXiv preprint arXiv:2503.08663",year="2025",eprint="2503.08663",url="https://arxiv.org/abs/2503.08663")),
 ("asimov2","misc",dict(author="{ASIMOV Benchmark}",title="ASIMOV Benchmark v2",year="2025",howpublished="Online",url="https://asimov-benchmark.github.io/v2/")),
 ("chen2024bgem3","inproceedings",dict(author="Chen, Jianlv and Xiao, Shitao and Zhang, Peitian and Luo, Kun and Lian, Defu and Liu, Zheng",title="M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation",booktitle="Findings of the Association for Computational Linguistics: ACL 2024",year="2024",url="https://aclanthology.org/2024.findings-acl.137/")),
 ("campello2013","inproceedings",dict(author="Campello, Ricardo J. G. B. and Moulavi, Davoud and Sander, J{\\\"o}rg",title="Density-Based Clustering Based on Hierarchical Density Estimates",booktitle="Pacific-Asia Conference on Knowledge Discovery and Data Mining (PAKDD)",year="2013",doi="10.1007/978-3-642-37456-2_14")),
 ("hdbscan2017","article",dict(author="McInnes, Leland and Healy, John and Astels, Steve",title="hdbscan: Hierarchical density based clustering",journal="Journal of Open Source Software",volume="2",number="11",pages="205",year="2017",doi="10.21105/joss.00205")),
 ("umap2018","article",dict(author="McInnes, Leland and Healy, John and Melville, James",title="UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction",journal="arXiv preprint arXiv:1802.03426",year="2018",eprint="1802.03426",url="https://arxiv.org/abs/1802.03426")),
 ("grootendorst2022","article",dict(author="Grootendorst, Maarten",title="BERTopic: Neural topic modeling with a class-based TF-IDF procedure",journal="arXiv preprint arXiv:2203.05794",year="2022",eprint="2203.05794",url="https://arxiv.org/abs/2203.05794")),
 ("dempster1977","article",dict(author="Dempster, Arthur P. and Laird, Nan M. and Rubin, Donald B.",title="Maximum Likelihood from Incomplete Data via the EM Algorithm",journal="Journal of the Royal Statistical Society: Series B (Methodological)",volume="39",number="1",pages="1--22",year="1977",doi="10.1111/j.2517-6161.1977.tb01600.x")),
 ("dhillon2001","article",dict(author="Dhillon, Inderjit S. and Modha, Dharmendra S.",title="Concept Decompositions for Large Sparse Text Data Using Clustering",journal="Machine Learning",volume="42",number="1--2",pages="143--175",year="2001",doi="10.1023/A:1007612920971")),
 ("weidinger2021","article",dict(author="Weidinger, Laura and Mellor, John and Rauh, Maribeth and others",title="Ethical and social risks of harm from Language Models",journal="arXiv preprint arXiv:2112.04359",year="2021",eprint="2112.04359",url="https://arxiv.org/abs/2112.04359")),
 ("slattery2024","article",dict(author="Slattery, Peter and Saeri, Alexander K. and Grundy, Emily A. C. and others",title="The AI Risk Repository: A Comprehensive Meta-Review, Database, and Taxonomy of Risks From Artificial Intelligence",journal="arXiv preprint arXiv:2408.12622",year="2024",eprint="2408.12622",url="https://arxiv.org/abs/2408.12622")),
 ("chan2023","inproceedings",dict(author="Chan, Alan and Salganik, Rebecca and Markelius, Alva and others",title="Harms from Increasingly Agentic Algorithmic Systems",booktitle="Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency (FAccT)",year="2023",doi="10.1145/3593013.3594033",eprint="2302.10329",url="https://arxiv.org/abs/2302.10329")),
 ("askell2021","article",dict(author="Askell, Amanda and Bai, Yuntao and Chen, Anna and others",title="A General Language Assistant as a Laboratory for Alignment",journal="arXiv preprint arXiv:2112.00861",year="2021",eprint="2112.00861",url="https://arxiv.org/abs/2112.00861")),
 ("bai2022","article",dict(author="Bai, Yuntao and Kadavath, Saurav and Kundu, Sandipan and others",title="Constitutional AI: Harmlessness from AI Feedback",journal="arXiv preprint arXiv:2212.08073",year="2022",eprint="2212.08073",url="https://arxiv.org/abs/2212.08073")),
 ("hendrycks2023","article",dict(author="Hendrycks, Dan and Mazeika, Mantas and Woodside, Thomas",title="An Overview of Catastrophic AI Risks",journal="arXiv preprint arXiv:2306.12001",year="2023",eprint="2306.12001",url="https://arxiv.org/abs/2306.12001")),
 ("bommasani2021","article",dict(author="Bommasani, Rishi and Hudson, Drew A. and Adeli, Ehsan and others",title="On the Opportunities and Risks of Foundation Models",journal="arXiv preprint arXiv:2108.07258",year="2021",eprint="2108.07258",url="https://arxiv.org/abs/2108.07258")),
 ("amodei2016","article",dict(author="Amodei, Dario and Olah, Chris and Steinhardt, Jacob and Christiano, Paul and Schulman, John and Man{\\'e}, Dan",title="Concrete Problems in AI Safety",journal="arXiv preprint arXiv:1606.06565",year="2016",eprint="1606.06565",url="https://arxiv.org/abs/1606.06565")),
 ("yampolskiy2016","inproceedings",dict(author="Yampolskiy, Roman V.",title="Taxonomy of Pathways to Dangerous Artificial Intelligence",booktitle="AAAI Workshop",year="2016",eprint="1511.03246",url="https://arxiv.org/abs/1511.03246")),
 ("critch2020","article",dict(author="Critch, Andrew and Krueger, David",title="AI Research Considerations for Human Existential Safety (ARCHES)",journal="arXiv preprint arXiv:2006.04948",year="2020",eprint="2006.04948",url="https://arxiv.org/abs/2006.04948")),
 ("oecd2022class","techreport",dict(author="{OECD}",title="OECD Framework for the Classification of AI Systems",institution="OECD Digital Economy Papers No. 323",year="2022",doi="10.1787/cb6d9eca-en")),
 ("oecd2024incidents","techreport",dict(author="{OECD}",title="Defining AI incidents and related terms",institution="OECD Artificial Intelligence Papers No. 16",year="2024",doi="10.1787/d1a8d965-en")),
 ("shevlane2023","article",dict(author="Shevlane, Toby and Farquhar, Sebastian and Garfinkel, Ben and others",title="Model evaluation for extreme risks",journal="arXiv preprint arXiv:2305.15324",year="2023",eprint="2305.15324",url="https://arxiv.org/abs/2305.15324")),
 ("gabriel2024","article",dict(author="Gabriel, Iason and Manzini, Arianna and Keeling, Geoff and others",title="The Ethics of Advanced AI Assistants",journal="arXiv preprint arXiv:2404.16244",year="2024",eprint="2404.16244",url="https://arxiv.org/abs/2404.16244")),
 ("openai2025prep","techreport",dict(author="{OpenAI}",title="Preparedness Framework (Version 2)",institution="OpenAI",year="2025",url="https://openai.com/index/updating-our-preparedness-framework/")),
 ("anthropic2024rsp","techreport",dict(author="{Anthropic}",title="Anthropic's Responsible Scaling Policy",institution="Anthropic",year="2025",url="https://www.anthropic.com/responsible-scaling-policy")),
 ("deepmind2025fsf","techreport",dict(author="{Google DeepMind}",title="Frontier Safety Framework (Version 2.0)",institution="Google DeepMind",year="2025",url="https://deepmind.google/discover/blog/updating-the-frontier-safety-framework/")),
 ("shavit2023","techreport",dict(author="Shavit, Yonadav and Agarwal, Sandhini and Brundage, Miles and others",title="Practices for Governing Agentic AI Systems",institution="OpenAI",year="2023",url="https://openai.com/research/practices-for-governing-agentic-ai-systems")),
 ("chan2024","inproceedings",dict(author="Chan, Alan and Ezell, Carson and Kaufmann, Max and others",title="Visibility into AI Agents",booktitle="Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency (FAccT)",year="2024",doi="10.1145/3630106.3658948",eprint="2401.13138",url="https://arxiv.org/abs/2401.13138")),
 ("benton2024","article",dict(author="Benton, Joe and Wagner, Misha and Christiansen, Eric and others",title="Sabotage Evaluations for Frontier Models",journal="arXiv preprint arXiv:2410.21514",year="2024",eprint="2410.21514",url="https://arxiv.org/abs/2410.21514")),
 ("iso21448","techreport",dict(author="{International Organization for Standardization}",title="ISO 21448:2022 --- Road vehicles: Safety of the intended functionality (SOTIF)",institution="ISO",year="2022",url="https://www.iso.org/standard/77490.html")),
 ("ul4600","techreport",dict(author="{Underwriters Laboratories}",title="ANSI/UL 4600: Standard for Evaluation of Autonomous Products",institution="UL Standards",year="2023",url="https://www.shopulstandards.com/ProductDetail.aspx?productId=UL4600")),
 ("altman1999","book",dict(author="Altman, Eitan",title="Constrained Markov Decision Processes",publisher="Chapman \\& Hall/CRC",year="1999")),
 ("anderson2018","article",dict(author="Anderson, Peter and Chang, Angel and Chaplot, Devendra Singh and Dosovitskiy, Alexey and Gupta, Saurabh and Koltun, Vladlen and Kosecka, Jana and Malik, Jitendra and Mottaghi, Roozbeh and Savva, Manolis and Zamir, Amir R.",title="On Evaluation of Embodied Navigation Agents",journal="arXiv preprint arXiv:1807.06757",year="2018",eprint="1807.06757",url="https://arxiv.org/abs/1807.06757")),
 ("asimov1950","book",dict(author="Asimov, Isaac",title="I, Robot",publisher="Gnome Press",year="1950")),
 ("murphy2009","article",dict(author="Murphy, Robin and Woods, David D.",title="Beyond Asimov: The Three Laws of Responsible Robotics",journal="IEEE Intelligent Systems",volume="24",number="4",pages="14--20",year="2009",doi="10.1109/MIS.2009.69")),
 ("russell2019","book",dict(author="Russell, Stuart",title="Human Compatible: Artificial Intelligence and the Problem of Control",publisher="Viking",year="2019")),
 ("christiano2017","inproceedings",dict(author="Christiano, Paul and Leike, Jan and Brown, Tom B. and Martic, Miljan and Legg, Shane and Amodei, Dario",title="Deep Reinforcement Learning from Human Preferences",booktitle="Advances in Neural Information Processing Systems (NeurIPS)",year="2017",eprint="1706.03741",url="https://arxiv.org/abs/1706.03741")),
 ("ouyang2022","inproceedings",dict(author="Ouyang, Long and Wu, Jeff and Jiang, Xu and Almeida, Diogo and Wainwright, Carroll L. and Mishkin, Pamela and others",title="Training Language Models to Follow Instructions with Human Feedback",booktitle="Advances in Neural Information Processing Systems (NeurIPS)",year="2022",eprint="2203.02155",url="https://arxiv.org/abs/2203.02155")),
 ("casper2023","article",dict(author="Casper, Stephen and Davies, Xander and Shi, Claudia and others",title="Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback",journal="Transactions on Machine Learning Research (arXiv:2307.15217)",year="2023",eprint="2307.15217",url="https://arxiv.org/abs/2307.15217")),
 ("kaplan1981","article",dict(author="Kaplan, Stanley and Garrick, B. John",title="On the Quantitative Definition of Risk",journal="Risk Analysis",volume="1",number="1",pages="11--27",year="1981",doi="10.1111/j.1539-6924.1981.tb01350.x")),
 ("collins2005","article",dict(author="Collins, Steve and Ruina, Andy and Tedrake, Russ and Wisse, Martijn",title="Efficient Bipedal Robots Based on Passive-Dynamic Walkers",journal="Science",volume="307",number="5712",pages="1082--1085",year="2005",doi="10.1126/science.1107799")),
 ("achiam2017","inproceedings",dict(author="Achiam, Joshua and Held, David and Tamar, Aviv and Abbeel, Pieter",title="Constrained Policy Optimization",booktitle="Proceedings of the 34th International Conference on Machine Learning (ICML)",year="2017",eprint="1705.10528",url="https://arxiv.org/abs/1705.10528")),
]

ORDER = ["author","title","journal","booktitle","publisher","institution","volume","number","pages","year","doi","eprint","archivePrefix","url","howpublished","note"]
def bib_entry(key,typ,f):
    if "eprint" in f: f.setdefault("archivePrefix","arXiv")
    lines=[f"@{typ}{{{key},"]
    for k in ORDER:
        if k in f and f[k]:
            lines.append(f"  {k} = {{{f[k]}}},")
    lines.append("}")
    return "\n".join(lines)

bib="% Physical AI Risk Taxonomy -- Technical Report references\n% Import into Zotero: File > Import (BibTeX).\n\n"
bib+="\n\n".join(bib_entry(k,t,dict(f)) for k,t,f in E)+"\n"
open(os.path.join(OUT,"references.bib"),"w",encoding="utf-8").write(bib)

# ---- RIS ----
TYPE={"article":"JOUR","inproceedings":"CPAPER","book":"BOOK","techreport":"RPRT","misc":"ELEC"}
def strip(s):
    return s.replace("{","").replace("}","").replace("\\&","&").replace("\\'","").replace('\\"',"").replace("\\v ","").replace("--","-")
def ris_entry(key,typ,f):
    o=[f"TY  - {TYPE[typ]}"]
    for a in strip(f.get('author','')).split(" and "):
        if a.strip(): o.append(f"AU  - {a.strip()}")
    o.append(f"TI  - {strip(f.get('title',''))}")
    if f.get('journal'): o.append(f"JO  - {strip(f['journal'])}")
    if f.get('booktitle'): o.append(f"T2  - {strip(f['booktitle'])}")
    if f.get('publisher'): o.append(f"PB  - {strip(f['publisher'])}")
    if f.get('institution'): o.append(f"PB  - {strip(f['institution'])}")
    if f.get('volume'): o.append(f"VL  - {f['volume']}")
    if f.get('number'): o.append(f"IS  - {f['number']}")
    if f.get('pages'): o.append(f"SP  - {strip(f['pages'])}")
    if f.get('year'): o.append(f"PY  - {f['year']}")
    if f.get('doi'): o.append(f"DO  - {f['doi']}")
    if f.get('url'): o.append(f"UR  - {f['url']}")
    o.append("ER  - ")
    return "\n".join(o)
ris="\n".join(ris_entry(k,t,dict(f)) for k,t,f in E)+"\n"
open(os.path.join(OUT,"references.ris"),"w",encoding="utf-8").write(ris)
print(f"wrote references.bib and references.ris  ({len(E)} entries)")
