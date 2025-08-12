{%@ set y = data | to_yaml @%}{%@ set back = y | from_yaml @%}Name={{@ back.name @}},Value={{@ back.value @}}
