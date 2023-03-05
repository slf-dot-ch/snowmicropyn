import pandas as pd
import xml.etree.ElementTree as ET

_ns = {"caaml": "http://caaml.org/Schemas/SnowProfileIACS/v6.0.3"}

def parse_grainshape(caaml_file: str):
    tree = ET.parse(caaml_file)
    root = tree.getroot()
    strat = root.find("caaml:snowProfileResultsOf", _ns) 
    strat = strat.find("caaml:SnowProfileMeasurements", _ns)
    strat = strat.find("caaml:stratProfile", _ns)

    extract_list = ["depthTop", "thickness", "grainFormPrimary"]
    layer_list = []
    for layer in strat.findall("caaml:Layer", _ns):
        attr_list = []
        for attr in extract_list:
            val = layer.find(f"caaml:{attr}", _ns).text
            try:
                val = float(val)
            except:
                pass
            attr_list.append(val)
        layer_list.append(attr_list)

    return pd.DataFrame(layer_list, columns=extract_list)

if __name__ == "__main__":
    caaml_file = "../../data/rhossa/TraditionalProfiles/20151130/5wj-20151130_niViz6_81339.caaml"
    grain_samples = parse_grainshape(caaml_file)
    print(grain_samples)
