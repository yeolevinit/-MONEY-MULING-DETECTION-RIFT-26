import time
import pandas as pd

def format_response(scores, rings, node_patterns, node_ring_map, start_time, total_accounts, G, df, payroll_like=None, merchant_like=None):
    """
    Builds the full JSON response including suspicious_accounts, fraud_rings,
    summary, and graph_data (nodes + edges) required by the frontend.
    """
    payroll_set = set(payroll_like or [])
    merchant_set = set(merchant_like or [])
    suspicious_set = set(node for node, score in scores.items() if score >= 50)

    # ─────────────────────────────────────────────
    # 1. SUSPICIOUS ACCOUNTS
    # ─────────────────────────────────────────────
    suspicious_accounts = []
    for acc, score in scores.items():
        if score >= 50:
            suspicious_accounts.append({
                "account_id": str(acc),
                "suspicion_score": float(min(100.0, round(score, 2))),
                "detected_patterns": node_patterns.get(acc, []),
                "ring_id": node_ring_map.get(acc, "UNKNOWN")
            })

    suspicious_accounts.sort(key=lambda x: x["suspicion_score"], reverse=True)

    # ─────────────────────────────────────────────
    # 2. SUMMARY
    # ─────────────────────────────────────────────
    summary = {
        "total_accounts_analyzed": total_accounts,
        "suspicious_accounts_flagged": len(suspicious_accounts),
        "fraud_rings_detected": len(rings),
        "processing_time_seconds": round(time.time() - start_time, 2)
    }

    # ─────────────────────────────────────────────
    # 3. GRAPH DATA  — nodes
    # ─────────────────────────────────────────────
    graph_nodes = []
    for node in G.nodes():
        node_str = str(node)

        # Compute aggregated transaction stats from the dataframe
        sent_mask = df["sender_id"] == node_str
        recv_mask = df["receiver_id"] == node_str
        total_sent = float(df.loc[sent_mask, "amount"].sum())
        total_received = float(df.loc[recv_mask, "amount"].sum())
        total_transactions = int(sent_mask.sum() + recv_mask.sum())

        graph_nodes.append({
            "id": node_str,
            "label": node_str,
            "is_suspicious": node in suspicious_set or node_str in suspicious_set,
            "is_whitelisted": node in payroll_set or node in merchant_set,
            "suspicion_score": float(min(100.0, round(scores.get(node, 0), 2))),
            "ring_id": node_ring_map.get(node, None),
            "detected_patterns": node_patterns.get(node, []),
            "total_transactions": total_transactions,
            "total_sent": round(total_sent, 2),
            "total_received": round(total_received, 2)
        })

    # ─────────────────────────────────────────────
    # 4. GRAPH DATA — edges
    # ─────────────────────────────────────────────
    graph_edges = []
    for u, v, data in G.edges(data=True):
        ts = data.get("timestamp", "")
        # Convert pandas Timestamp to string if needed
        if hasattr(ts, "strftime"):
            ts = ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts = str(ts)

        graph_edges.append({
            "id": str(data.get("transaction_id", f"{u}-{v}")),
            "source": str(u),
            "target": str(v),
            "amount": float(data.get("amount", 0)),
            "timestamp": ts
        })

    return {
        "suspicious_accounts": suspicious_accounts,
        "fraud_rings": rings,
        "summary": summary,
        "graph_data": {
            "nodes": graph_nodes,
            "edges": graph_edges
        }
    }