# Week 3 Part 2: Testing, Monitoring & SLA Management

## Objectives
- Master the 4-layer testing hierarchy: Unit, Integration, Contract, and Golden Dataset Regression.
- Implement Data Contracts with Pandera schema validation as code.
- Design SLA contracts and query pipeline health KPIs.
- Study the Razorpay Payment Pipeline Before vs After Redesign.

## 1. The 4-Layer Testing Framework

1. **Unit Testing**: Tests isolated transformation functions (e.g. string cleaner, tax calculation).
2. **Integration Testing**: Tests raw-to-silver loading with mock database dependencies.
3. **Contract Testing**: Validates column names, data types, null constraints, and regex rules using Pandera as code.
4. **Regression Testing**: Compares current pipeline run outputs against a Golden Dataset baseline to prevent silent logic regressions.

---

## 2. SLA Monitoring & Health Audit
Track pipeline KPIs in `pipeline_run_audit`:
- **Freshness**: Maximum lag between event timestamp and Gold load timestamp.
- **Completeness**: Source count vs Target loaded count reconciliation.
- **Success Rate**: Percentage of successful batch runs over 30 days.
- **Throughput**: Records processed per second.
