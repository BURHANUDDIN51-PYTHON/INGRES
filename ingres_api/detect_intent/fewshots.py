FEW_SHOT_EXAMPLE = [
  {
    "query": "Show all the exploited cities in Rajasthan",
    "response": {
      "intent": "list_units_by_category",
      "entities": { "state": "Rajasthan", "category": "Over-exploited", "year": 2023, "limit": 50 },
      "confidence": 0.93
    }
  },
  {
    "query": "What was the annual recharge in the Jaipur district in 2023?",
    "response": {
      "intent": "get_data_for_unit",
      "entities": { "district": "Jaipur", "metric": "annual_recharge", "year": 2023 },
      "confidence": 0.96
    }
  },
  {
    "query": "Compare the stage of extraction in Maharashtra and Gujarat.",
    "response": {
      "intent": "compare_data",
      "entities": { "states": ["Maharashtra", "Gujarat"], "metric": "stage_of_extraction", "year": 2023 },
      "confidence": 0.94
    }
  },
  {
    "query": "Which blocks in Rajasthan have an annual extraction over 500 million cubic meters?",
    "response": {
      "intent": "find_units_by_metric_value",
      "entities": { "state": "Rajasthan", "metric": "annual_extraction", "operator": "greater_than", "value": 500 },
      "confidence": 0.92
    }
  },
 
  {
    "query": "Compare extraction between Punjab and Haryana for 2021",
    "response": {
      "intent": "compare_states_extraction",
      "entities": { "states": ["Punjab", "Haryana"], "year": 2021 },
      "confidence": 0.94
    }
  },
 
]



