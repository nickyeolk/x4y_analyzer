"""
OpenTelemetry configuration for distributed tracing.
Sets up tracer and meter for agent observability.
"""

from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource

from config.settings import settings


# Global tracer and meter instances
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None


def configure_observability() -> None:
    """Configure OpenTelemetry tracing and metrics."""
    global _tracer, _meter

    if not settings.otel_enabled:
        # Use no-op implementations if observability is disabled
        _tracer = trace.get_tracer(__name__)
        _meter = metrics.get_meter(__name__)
        return

    # Create resource with service information
    resource = Resource.create(
        {
            "service.name": "agentland",
            "service.version": "0.1.0",
            "deployment.environment": settings.app_env,
        }
    )

    # Configure tracing
    if settings.otel_exporter == "console":
        # Console exporter for development
        span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    else:
        # Could add Jaeger or OTLP exporters here
        span_processor = BatchSpanProcessor(ConsoleSpanExporter())

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    _tracer = trace.get_tracer("agentland.tracer", "0.1.0")

    # Configure metrics
    if settings.otel_exporter == "console":
        metric_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60000,  # Export every 60 seconds
        )
    else:
        metric_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60000,
        )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter("agentland.meter", "0.1.0")


def get_tracer() -> trace.Tracer:
    """
    Get the configured tracer instance.

    Returns:
        OpenTelemetry tracer
    """
    if _tracer is None:
        configure_observability()
    return _tracer  # type: ignore


def get_meter() -> metrics.Meter:
    """
    Get the configured meter instance.

    Returns:
        OpenTelemetry meter
    """
    if _meter is None:
        configure_observability()
    return _meter  # type: ignore
