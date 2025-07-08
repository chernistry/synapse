from typing import List, Dict, Any
from src.simulation.continuous_map import generate_continuous_scenario
from src.agents.static_agent import StaticAgent
from src.agents.synapse_agent import SYNAPSEAgent
from src.analysis.path_analyzer import analyze_path_continuous
from src.analysis.reporting import generate_report

def run_single_scenario(scenario_id: str, scenario_params: Dict, agents: List[Any]) -> List[Dict]:
    """
    Runs a single continuous scenario for a list of agents.
    """
    print(f"\n--- Running Scenario: {scenario_id} ---")
    problem_map = generate_continuous_scenario(scenario_params)
    
    results = []
    for agent in agents:
        # For the SYNAPSE agent, allow it to adapt to the map before solving.
        if isinstance(agent, SYNAPSEAgent):
            agent.adapt(context={"problem_map": problem_map, "scenario_id": scenario_id})
            
        path = agent.solve(problem_map)
        
        raw_perf = {}
        if path:
            raw_perf = analyze_path_continuous(path, problem_map)
            
        results.append({
            'scenario_id': scenario_id,
            'scenario_type': scenario_params.get('type', 'unknown'),
            'agent': agent.name,
            'path_found': bool(path),
            'raw_perf': raw_perf
        })
    
    return results

def run_experiment():
    """
    Main entry point for running the new continuous SYNAPSE experiment.
    """
    print("SYNAPSE Continuous Experiment")
    print("=" * 30)
    
    # 1. Define the suite of scenarios to test
    scenarios = {
        "S1_DynamicWind": {"type": "dynamic_wind", "dimensions": (100, 100)},
        # Future scenarios can be added here
        # "S2_HighClutter": {"type": "high_clutter", "dimensions": (120, 120)},
    }
    
    # 2. Instantiate agents
    agents = [StaticAgent(), SYNAPSEAgent()]
    
    # 3. Run all scenarios
    all_results = []
    for scenario_id, params in scenarios.items():
        scenario_results = run_single_scenario(scenario_id, params, agents)
        all_results.extend(scenario_results)
    
    # 4. Generate final report
    print("\n--- Generating Final Report ---")
    
    # The new reporting function needs a slightly different data structure.
    # We will flatten the raw_perf dictionary for the CSV.
    report_data = []
    for res in all_results:
        flat_row = {
            'scenario_id': res['scenario_id'],
            'scenario_type': res['scenario_type'],
            'agent': res['agent'],
            'path_found': res['path_found'],
        }
        # Add performance metrics with a 'raw_' prefix
        for key, value in res.get('raw_perf', {}).items():
            flat_row[f'raw_{key}'] = value
        report_data.append(flat_row)
        
    generate_report(report_data)
    
    print("=" * 30)
    print("Experiment finished.")


if __name__ == "__main__":
    run_experiment() 