from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="StatsTypesStatsModel")


@attr.s(auto_attribs=True)
class StatsTypesStatsModel:
    """
    Attributes:
        total_webhooks_delivered (float): The total amount of webhooks delivered across all streams
        total_webhooks_failed (float): The total amount of failed webhooks across all streams
        total_logs_processed (float): The total amount of logs processed across all streams, this includes failed
            webhooks
        total_txs_processed (float): The total amount of txs processed across all streams, this includes failed webhooks
        total_txs_internal_processed (float): The total amount of internal txs processed across all streams, this
            includes failed webhooks
    """

    total_webhooks_delivered: float
    total_webhooks_failed: float
    total_logs_processed: float
    total_txs_processed: float
    total_txs_internal_processed: float

    def to_dict(self) -> Dict[str, Any]:
        total_webhooks_delivered = self.total_webhooks_delivered
        total_webhooks_failed = self.total_webhooks_failed
        total_logs_processed = self.total_logs_processed
        total_txs_processed = self.total_txs_processed
        total_txs_internal_processed = self.total_txs_internal_processed

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "totalWebhooksDelivered": total_webhooks_delivered,
                "totalWebhooksFailed": total_webhooks_failed,
                "totalLogsProcessed": total_logs_processed,
                "totalTxsProcessed": total_txs_processed,
                "totalTxsInternalProcessed": total_txs_internal_processed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total_webhooks_delivered = d.pop("totalWebhooksDelivered")

        total_webhooks_failed = d.pop("totalWebhooksFailed")

        total_logs_processed = d.pop("totalLogsProcessed")

        total_txs_processed = d.pop("totalTxsProcessed")

        total_txs_internal_processed = d.pop("totalTxsInternalProcessed")

        stats_types_stats_model = cls(
            total_webhooks_delivered=total_webhooks_delivered,
            total_webhooks_failed=total_webhooks_failed,
            total_logs_processed=total_logs_processed,
            total_txs_processed=total_txs_processed,
            total_txs_internal_processed=total_txs_internal_processed,
        )

        return stats_types_stats_model
