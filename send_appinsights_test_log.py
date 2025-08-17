import logging
import time
import random
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer
from opencensus.ext.azure.metrics_exporter import MetricsExporter
from opencensus.stats import stats as stats_module
from opencensus.stats import measure as measure_module
from opencensus.stats import view as view_module
from opencensus.stats import aggregation as aggregation_module
from opencensus.tags import tag_map as tag_map_module

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string="InstrumentationKey=861d0aa5-d6cb-4b4b-8265-aa123a4ab3e0;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"
))

print("Sending diverse telemetry...")

# Send custom events
for i in range(5):
    logger.info(f"CustomEvent: TechnicianSubmittedDefect {i}", extra={'custom_dimensions': {'eventType': 'TechnicianSubmittedDefect', 'defectId': i}})
    time.sleep(0.1)

# Send exceptions
try:
    1 / 0
except Exception as e:
    logger.exception("Simulated exception for Application Insights")

# Send traces at different levels
for i in range(3):
    logger.debug(f"Debug trace {i}")
    logger.warning(f"Warning trace {i}")

# Send custom metric
exporter = MetricsExporter(
    connection_string="InstrumentationKey=861d0aa5-d6cb-4b4b-8265-aa123a4ab3e0;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"
)
stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

m_latency_ms = measure_module.MeasureFloat("demo_latency", "Demo request latency", "ms")
latency_view = view_module.View("demo_latency_view", "Demo request latency view", ["environment"], m_latency_ms, aggregation_module.DistributionAggregation([0, 100, 200, 400, 800, 1600]))
view_manager.register_view(latency_view)

for i in range(10):
    mmap = stats_recorder.new_measurement_map()
    tmap = tag_map_module.TagMap()
    tmap["environment"] = "demo"
    latency = random.randint(50, 1500)
    mmap.measure_float_put(m_latency_ms, latency)
    mmap.record(tmap)
    time.sleep(0.1)

print("Diverse telemetry sent.")