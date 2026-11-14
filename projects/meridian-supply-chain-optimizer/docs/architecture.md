# Architecture

Input JSON → validation → source/warehouse/store/sink residual graph → repeated shortest augmenting paths → integer shipment plan → JSON report.

Each original edge receives a reverse residual edge with negative cost. Relaxation across residual edges permits rerouting earlier shipments, which is essential for correct min-cost optimization. Each augmentation saturates at least one residual edge or reaches requested demand; capacities remain integral.

For negative-cost residual cycles, this reference assumes the standard successive shortest-path invariant reached from an initially empty feasible flow with nonnegative forward costs. Performance is not suitable for large networks.
