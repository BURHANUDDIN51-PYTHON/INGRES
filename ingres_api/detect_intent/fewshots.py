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
    "query": "Thank you, that was helpful.",
    "response": {
      "intent": "thank_you",
      "entities": {},
      "confidence": 0.99
    }
  },
  {
    "query": "Show all the exploited cities in Rajsthaan",
    "response": {
      "intent": "list_units_by_category",
      "entities": { "state": "Rajasthan", "category": "Over-exploited", "year": 2023 },
      "confidence": 0.92
    }
  },
  {
    "query": "Udepur ke liye annual recharge batao 2022 ka",
    "response": {
      "intent": "get_data_for_unit",
      "entities": { "district": "Udaipur", "metric": "annual_recharge", "year": 2022 },
      "confidence": 0.94
    }
  },
  {
    "query": "What was ground level water for the Rajsthaan last year?",
    "response": {
      "intent": "get_state_metric",
      "entities": { "state": "Rajasthan", "metric": "stage_of_extraction", "year": 2024 },
      "confidence": 0.93
    }
  },
  {
    "query": "Get me the Kerila data for the last 5 years",
    "response": {
      "intent": "get_historical_data",
      "entities": { "state": "Kerala", "start_year": 2019, "end_year": 2024 },
      "confidence": 0.95
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
  {
    "query": "Top 5 districts with highest stage of extraction 2023",
    "response": {
      "intent": "find_units_by_metric_value",
      "entities": { "metric": "stage_of_extraction", "operator": "top_n", "value": 5, "year": 2023 },
      "confidence": 0.93
    }
  },
  {
    "query": "Mujhe help chahiye, kaise data check karun?",
    "response": {
      "intent": "general_help",
      "entities": {},
      "confidence": 0.96
    }
  },
  {
    "query": "Shukriya!",
    "response": {
      "intent": "thank_you",
      "entities": {},
      "confidence": 0.99
    }
  },
  {
    "query": "Who won the FIFA World Cup 2022?",
    "response": {
      "intent": "unsupported",
      "entities": {},
      "confidence": 0.99
    }
  }
]