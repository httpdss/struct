{%@ set j = data | to_json @%}{%@ set back = j | from_json @%}Kind={{@ back.kind @}},Count={{@ back.count @}}
