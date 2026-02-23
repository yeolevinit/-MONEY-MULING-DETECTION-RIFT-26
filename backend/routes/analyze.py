import time
from flask import Blueprint, request, jsonify
from services.graph_builder import build_graph
from services.cycle_detector import detect_cycles
from services.smurfing_detector import detect_smurfing
from services.shell_detector import detect_shells
from services.suspicion_engine import calculate_scores
from services.json_formatter import format_response
from utils.validators import validate_csv

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze", methods=["POST"])
def analyze_transactions():
    start_time = time.time()

    if 'file' not in request.files:
        return jsonify({"error": "CSV file required"}), 400

    file = request.files['file']

    try:
        df = validate_csv(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    G = build_graph(df)

    cycles = detect_cycles(G)

    # smurfing returns (suspicious_nodes, payroll_like, merchant_like, benford_violators)
    smurfing_data = detect_smurfing(G, df)
    suspicious_nodes, payroll_like, merchant_like, benford_violators = smurfing_data

    shell_chains = detect_shells(G, cycles)

    scores, rings, node_patterns, node_ring_map = calculate_scores(
        G, cycles, smurfing_data, shell_chains
    )

    response = format_response(
        scores,
        rings,
        node_patterns,
        node_ring_map,
        start_time,
        len(G.nodes),
        G=G,
        df=df,
        payroll_like=payroll_like,
        merchant_like=merchant_like
    )

    return jsonify(response)
