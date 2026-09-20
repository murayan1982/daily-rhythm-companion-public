enum ProductionBackendOperation {
  loadCharacters,
  loadSleepSummary,
  loadSleepProviderSelection,
  createAdvice,
  createTextChatSession,
  sendTextChatMessage,
  loadHistory,
  loadRecentSleepTrend,
  loadWeeklySleepSummary,
  loadWeeklyRhythmReport,
  loadMonthlyRhythmReport,
  loadFitbitConnectionStatus,
  startFitbitConnection,
  loadGoogleHealthConnectionGuidance,
}

enum ProductionBackendOperationDisposition {
  coreCandidate,
  healthPendingDecision,
}

enum ProductionBackendAccessDecision {
  allowCoreCandidate,
  denyHealthPendingDecision,
  denyUnknown,
}

const Map<ProductionBackendOperation, ProductionBackendOperationDisposition>
productionBackendOperationDispositions = {
  ProductionBackendOperation.loadCharacters:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadSleepSummary:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadSleepProviderSelection:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.createAdvice:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.createTextChatSession:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.sendTextChatMessage:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadHistory:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadRecentSleepTrend:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadWeeklySleepSummary:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadWeeklyRhythmReport:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadMonthlyRhythmReport:
      ProductionBackendOperationDisposition.coreCandidate,
  ProductionBackendOperation.loadFitbitConnectionStatus:
      ProductionBackendOperationDisposition.healthPendingDecision,
  ProductionBackendOperation.startFitbitConnection:
      ProductionBackendOperationDisposition.healthPendingDecision,
  ProductionBackendOperation.loadGoogleHealthConnectionGuidance:
      ProductionBackendOperationDisposition.healthPendingDecision,
};

const Set<ProductionBackendOperation> activeProductionBackendOperations = {
  ProductionBackendOperation.loadCharacters,
  ProductionBackendOperation.loadSleepSummary,
  ProductionBackendOperation.loadSleepProviderSelection,
  ProductionBackendOperation.createAdvice,
  ProductionBackendOperation.createTextChatSession,
  ProductionBackendOperation.sendTextChatMessage,
  ProductionBackendOperation.loadHistory,
  ProductionBackendOperation.loadRecentSleepTrend,
  ProductionBackendOperation.loadWeeklySleepSummary,
  ProductionBackendOperation.loadWeeklyRhythmReport,
  ProductionBackendOperation.loadMonthlyRhythmReport,
};

ProductionBackendOperationDisposition? productionBackendDispositionFor(
  Object operation,
) {
  if (operation is! ProductionBackendOperation) {
    return null;
  }
  return productionBackendOperationDispositions[operation];
}

ProductionBackendAccessDecision productionBackendAccessDecisionFor(
  Object operation,
) {
  return switch (productionBackendDispositionFor(operation)) {
    ProductionBackendOperationDisposition.coreCandidate =>
      ProductionBackendAccessDecision.allowCoreCandidate,
    ProductionBackendOperationDisposition.healthPendingDecision =>
      ProductionBackendAccessDecision.denyHealthPendingDecision,
    null => ProductionBackendAccessDecision.denyUnknown,
  };
}

bool isProductionBackendOperationAllowed(Object operation) =>
    productionBackendAccessDecisionFor(operation) ==
    ProductionBackendAccessDecision.allowCoreCandidate;

bool isActiveProductionBackendOperation(Object operation) =>
    isProductionBackendOperationAllowed(operation);
