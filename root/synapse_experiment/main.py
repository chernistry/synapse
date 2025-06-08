import pandas as pd
import numpy as np
import yaml
from pathlib import Path

import src.simulation.map as sim_map
from src.agents.static_agent import StaticAgent
from src.agents.synapse_agent import SYNAPSEAgent
import src.analysis.metrics as metrics
import src.analysis.reporting as reporting
from src.analysis.path_analyzer import analyze_path

CONFIG_PATH = Path(__file__).parent / "config.yml"

def load_config() -> dict:
    """Loads the YAML configuration file."""
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config

def generate_experiment_suite(config: dict) -> list[dict]:
    """Generates a list of scenario configurations based on the main config."""
    num_scenarios = config['num_scenarios']
    gen_params = config['scenario_generation']
    split = gen_params['split']
    
    scenarios = []
    
    # Calculate number of scenarios per type
    num_training = int(num_scenarios * split['training'])
    num_validation = int(num_scenarios * split['validation'])
    num_holdout = num_scenarios - num_training - num_validation
    
    scenario_counts = {
        'training': num_training,
        'validation': num_validation,
        'holdout': num_holdout
    }

    for set_type, count in scenario_counts.items():
        for i in range(count):
            dim_w = np.random.randint(gen_params['dimensions']['min'], gen_params['dimensions']['max'])
            dim_h = np.random.randint(gen_params['dimensions']['min'], gen_params['dimensions']['max'])
            
            # Ensure start/end points are not too close to the edge
            start_x = np.random.randint(5, dim_w // 4)
            start_y = np.random.randint(5, dim_h // 4)
            end_x = np.random.randint(dim_w * 3 // 4, dim_w - 5)
            end_y = np.random.randint(dim_h * 3 // 4, dim_h - 5)
            
            scenarios.append({
                'type': set_type,
                'id': f"{set_type}_{i+1}",
                'dimensions': (dim_w, dim_h),
                'start': (start_x, start_y),
                'end': (end_x, end_y),
                'num_obstacles': np.random.randint(gen_params['num_obstacles']['min'], gen_params['num_obstacles']['max']),
                'obstacle_size_range': (gen_params['obstacle_size']['min'], gen_params['obstacle_size']['max']),
                'is_holdout': set_type == 'holdout' # Flag for special logic
            })
            
    return scenarios

def normalize_results(all_run_results: list[dict]) -> list[dict]:
    """Normalizes scores across all runs to a 0-1 scale where 1 is best."""
    if not all_run_results:
        return []

    combined_data = {
        'time': [], 'energy': [], 'safety': [], 'payload_integrity': []
    }
    for run in all_run_results:
        for key in combined_data.keys():
            combined_data[key].append(run[key])
    
    min_max = {key: (min(values), max(values)) for key, values in combined_data.items()}

    final_normalized_results = []
    for res in all_run_results:
        norm_res = {}
        for key, value in res.items():
            min_v, max_v = min_max[key]
            if max_v - min_v == 0:
                norm_res[key] = 1.0
            else:
                # Lower is better for these metrics, so invert the score
                norm_res[key] = 1.0 - ((value - min_v) / (max_v - min_v))
        final_normalized_results.append(norm_res)
    
    return final_normalized_results


def run_single_scenario(scenario_params: dict, agents: list) -> list[dict]:
    """Runs the full experiment for a single scenario configuration."""
    print(f"  Running Scenario: {scenario_params.get('id', 'N/A')}...")
    
    scenario_map = sim_map.generate_scenario(scenario_params)
    
    results = []
    for agent in agents:
        path = agent.solve(scenario_map)
        path_perf = analyze_path(path, scenario_map)
        results.append({
            'scenario_id': scenario_params['id'],
            'scenario_type': scenario_params['type'],
            'agent': agent.name,
            'path_found': True if path else False,
            'path_length': path_perf['time'],
            'energy': path_perf['energy'],
            'safety': path_perf['safety'],
            'payload_integrity': path_perf['payload_integrity'],
            # Raw performance data for normalization
            'raw_perf': path_perf
        })
    
    return results


def run_experiment():
    """
    Main entry point for running the SYNAPSE synthetic experiment.
    """
    config = load_config()
    np.random.seed(config['random_seed'])
    
    print("SYNAPSE Synthetic Experiment")
    print("=" * 30)
    
    # --- Phase 1: Generate Scenario Suite ---
    print("Phase 1: Generating scenario suite...")
    scenarios = generate_experiment_suite(config)
    print(f"Generated {len(scenarios)} scenarios.")
    
    # --- Phase 2: Instantiate Agents ---
    agents = [StaticAgent(), SYNAPSEAgent()]
    all_results = []
    
    # --- Phase 3: Run All Scenarios ---
    print("\nPhase 3: Running all scenarios...")
    for params in scenarios:
        scenario_results = run_single_scenario(params, agents)
        all_results.extend(scenario_results)
    print("All scenarios complete.")

    # --- Phase 4: Calculate SRS and Normalize ---
    print("\nPhase 4: Calculating SRS and normalizing results...")
    raw_perf_data = [res['raw_perf'] for res in all_results]
    normalized_perf = normalize_results(raw_perf_data)
    
    for i, result in enumerate(all_results):
        result['normalized_perf'] = normalized_perf[i]
        agent_code_path = f"src/agents/{result['agent'].lower().replace('agent', '_agent')}.py"
        result['srs'] = metrics.calculate_srs(agent_code_path, config['srs_weights'])

    # --- Phase 5: Calculate Final PPS ---
    print("\nPhase 5: Calculating final PPS...")
    for result in all_results:
        result['pps'] = metrics.calculate_pps(result['normalized_perf'], config['final_pps_weights'])

    # --- Phase 6: Generate Report ---
    print("\nPhase 6: Generating final report...")
    reporting.generate_report(all_results)
    
    print("=" * 30)
    print("Experiment finished.")


if __name__ == "__main__":
    run_experiment() 