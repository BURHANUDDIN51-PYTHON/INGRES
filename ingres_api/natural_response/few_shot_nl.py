FEW_SHOT_EXAMPLES=[

  {
    "intent": "definition",
    "query": "What does semi-critical mean?",
    "rawData": {
      "term": "Semi-critical",
      "definition": "70–90% of groundwater is used, but some availability remains."
    },
    "expected_output": {
      "nl_response": "Semi-critical means 70–90% of groundwater is used, but some availability still remains.",
      "visualization_data": {}
    }
  },
  
  {
    "intent": "compare_states_extraction",
    "query": "Compare groundwater extraction between Maharashtra and Gujarat and show me a chart",
    "rawData": {
      "Maharashtra": 450,
      "Gujarat": 380
    },
    "expected_output": {
      "nl_response": "Maharashtra has higher groundwater extraction (450 units) compared to Gujarat (380 units).",
      "visualization_data": {
        "type": "bar",
        "labels": ["Maharashtra", "Gujarat"],
        "data": [450, 380],
        "x_axis": "State",
        "y_axis": "Groundwater Extraction"
      }
    }
  },

  {
    "intent": "get_historical_data",
    "query": "Show me groundwater history for District A",
    "rawData": [
      {"year": 2020, "status": "Safe"},
      {"year": 2021, "status": "Semi-critical"},
      {"year": 2022, "status": "Critical"}
    ],
    "expected_output": {
      "nl_response": "District A moved from Safe in 2020 to Semi-critical in 2021, and became Critical by 2022.",
      "visualization_data": {}
    }
  },
 
  {
    "intent": "general_help",
    "query": "Can you help me?",
    "rawData": {},
    "expected_output": {
      "nl_response": "Sure! You can ask me about groundwater status, availability, historical data, and comparisons between states or districts.",
      "visualization_data": {}
    }
  },
]


