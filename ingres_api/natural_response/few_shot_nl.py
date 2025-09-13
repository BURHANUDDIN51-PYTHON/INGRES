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
    "intent": "list_units_by_category",
    "query": "List all districts in the critical category",
    "rawData": [
      {"district": "District A", "status": "Critical"},
      {"district": "District B", "status": "Critical"}
    ],
    "expected_output": {
      "nl_response": "Districts in the critical category are District A and District B.",
      "visualization_data": {}
    }
  },
  {
    "intent": "list_units_by_condition",
    "query": "Show blocks with extraction above 90%",
    "rawData": [
      {"block": "Block X", "extraction": 95},
      {"block": "Block Y", "extraction": 92}
    ],
    "expected_output": {
      "nl_response": "Blocks with extraction above 90% are Block X (95%) and Block Y (92%).",
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
    "intent": "compare_categories_in_state",
    "query": "Show me category distribution in Rajasthan",
    "rawData": {
      "Safe": 120,
      "Semi-critical": 80,
      "Critical": 40,
      "Over-exploited": 25
    },
    "expected_output": {
      "nl_response": "In Rajasthan, there are 120 safe units, 80 semi-critical units, 40 critical units, and 25 over-exploited units.",
      "visualization_data": {}
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
    "intent": "get_state_metric",
    "query": "What is groundwater availability in State A?",
    "rawData": {
      "state": "State A",
      "availability": "1500 MCM"
    },
    "expected_output": {
      "nl_response": "The groundwater availability in State A is 1500 MCM.",
      "visualization_data": {}
    }
  },
  {
    "intent": "get_data_for_unit",
    "query": "Give me the status of District A",
    "rawData": {
      "district": "District A",
      "status": "Critical"
    },
    "expected_output": {
      "nl_response": "District A is in the Critical category.",
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
  {
    "intent": "thank_you",
    "query": "Thanks a lot!",
    "rawData": {},
    "expected_output": {
      "nl_response": "You’re welcome! Happy to help.",
      "visualization_data": {}
    }
  },

]
