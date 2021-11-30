import testing_utils
import re

import text_utils



def test_template_regexps(qtbot):
    template_output = """
{{Text}}
<hypertts-template-advanced>
field1 = template_fields['Text']
field2 = template_fields['Extra']
result = f"{field1} {field2}"
</hypertts-template-advanced>
"""
    expected_content = """field1 = template_fields['Text']
field2 = template_fields['Extra']
result = f"{field1} {field2}"
""".strip()
    actual_content = text_utils.extract_advanced_template(template_output)
    assert actual_content == expected_content

    template_output = """
{{Text}}
<hypertts-template>{Text} {Extra}</hypertts-template>
"""
    expected_content = """{Text} {Extra}"""
    actual_content = text_utils.extract_simple_template(template_output)
    assert actual_content == expected_content    


    template_output = """
{{Text}}
<hypertts-template>
{Text} {Extra}
</hypertts-template>
"""
    expected_content = """{Text} {Extra}"""
    actual_content = text_utils.extract_simple_template(template_output)
    assert actual_content == expected_content        
