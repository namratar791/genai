import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

type AgentName =
  | 'orchestrator'
  | 'behavior_agent'
  | 'location_agent'
  | 'merchant_agent'
  | 'device_agent'
  | 'vpn_agent'
  | 'merge_node'
  | 'policy_node'
  | 'confidence_node'
  | 'action_node'
  | 'guardrail_node'
  | 'human_review'
  | 'system';

interface FraudRunCreateResponse {
  run_id: string;
  status: string;
}

interface UiEvent {
  sequence: number;
  event_type: 'agent_update' | 'agent_result' | 'final_response';
  agent: string;
  status: 'working' | 'waiting' | 'completed' | 'failed';
  message: string;
  confidence_score?: number | null;
  issues?: string[];
  handoff_to?: string | null;
  final_action?: string | null;
  final_confidence?: number | null;
  final_output?: Record<string, any> | null;
}

interface FraudNextResponse {
  run_id: string;
  done: boolean;
  status: 'working' | 'waiting' | 'completed' | 'failed';
  delivered_count: number;
  ui_events: UiEvent[];
}

interface ChatMessage {
  sequence: number;
  agent: AgentName;
  title: string;
  emoji: string;
  text: string;
  status: string;
  confidence?: number | null;
  issues?: string[] | null;
  finalAction?: string | null;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  apiBase = 'http://127.0.0.1:8000';

  runId: string | null = null;
  isRunning = false;
  waitingForNext = false;
  done = false;

  transaction = {
    transaction_id: 'TXN123',
    amount: 2500,
    merchant: 'Amazon',
    city: 'New York',
    previous_city: 'Boston',
    known_device: false,
    device_trust_score: 0.35,
    vpn_suspected: true
  };

  messages: ChatMessage[] = [];
  awaitingHumanReview = false;
  reviewConfidence: number | null = null;
  reviewReason = '';

  async startRun(): Promise<void> {
    this.resetUi();

    try {
      this.isRunning = true;

      const res = await fetch(`${this.apiBase}/fraud/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.transaction)
      });

      if (!res.ok) {
        throw new Error(`Failed to create run: ${res.status}`);
      }

      const data: FraudRunCreateResponse = await res.json();
      this.runId = data.run_id;

      this.pushSystemMessage(
        `🟢 Session initialized. Run ID: ${this.runId}. Agentic analysis sequence ready.`
      );

      await this.autoPlay();
    } catch (error: any) {
      this.pushSystemMessage(`❌ Could not start run. ${error?.message || 'Unknown error'}`);
      this.isRunning = false;
    }
  }

  async getNextEvent(): Promise<void> {
    if (!this.runId || this.done || this.waitingForNext) return;

    try {
      this.waitingForNext = true;

      const res = await fetch(`${this.apiBase}/fraud/runs/${this.runId}/next`, {
        method: 'POST'
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to fetch next step: HTTP ${res.status} ${text}`);
      }

      const data: FraudNextResponse = await res.json();

      if (data.ui_events?.length) {
        for (const evt of data.ui_events) {
          this.messages.push(this.mapUiEventToMessage(evt));
          await this.sleep(700);

          if (
            (evt.agent === 'human_review' || evt.agent === 'hil_node') &&
            evt.status === 'waiting'
          ) {
            this.awaitingHumanReview = true;
            this.reviewConfidence = evt.final_confidence ?? evt.confidence_score ?? null;
            this.reviewReason = evt.message;
          }
        }
      }

      this.done = data.done;

      if (this.done) {
        this.isRunning = false;
        this.pushSystemMessage('✅ Analysis complete. All agents have finished speaking.');
      }
    } catch (error: any) {
      this.pushSystemMessage(`❌ Could not fetch next step. ${error?.message || 'Unknown error'}`);
      this.isRunning = false;
      this.done = true;
    } finally {
      this.waitingForNext = false;
    }
  }

  async autoPlay(): Promise<void> {
    if (!this.runId) return;

    this.isRunning = true;

    while (!this.done && !this.awaitingHumanReview) {
      await this.getNextEvent();

      if (!this.done && !this.awaitingHumanReview) {
        this.waitingForNext = true;
        await this.sleep(1500);
        this.waitingForNext = false;
      }
    }

    this.isRunning = false;
  }

  resetUi(): void {
    this.runId = null;
    this.isRunning = false;
    this.waitingForNext = false;
    this.done = false;
    this.messages = [];
    this.awaitingHumanReview = false;
    this.reviewConfidence = null;
    this.reviewReason = '';
  }

  private pushSystemMessage(text: string): void {
    this.messages.push({
      sequence: this.messages.length + 1,
      agent: 'system',
      title: 'System',
      emoji: '⚙️',
      text,
      status: 'completed'
    });
  }

  private mapUiEventToMessage(event: UiEvent): ChatMessage {
    const meta = this.getAgentMeta(event.agent);

    return {
      sequence: event.sequence,
      agent: meta.agent,
      title: meta.title,
      emoji: meta.emoji,
      text: event.message,
      status: event.status,
      confidence: event.final_confidence ?? event.confidence_score ?? null,
      issues: event.issues ?? [],
      finalAction: event.final_action ?? null
    };
  }

  async submitHumanDecision(decision: 'APPROVE' | 'HOLD' | 'ESCALATE'): Promise<void> {
    if (!this.runId) return;

    try {
      const res = await fetch(`${this.apiBase}/fraud/runs/${this.runId}/human-review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision })
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      this.awaitingHumanReview = false;
      this.pushSystemMessage(`🧑‍⚖️ Human reviewer selected: ${decision}`);
      await this.getNextEvent();
    } catch (error: any) {
      this.pushSystemMessage(`❌ Failed to submit human review. ${error?.message || 'Unknown error'}`);
    }
  }

  private getAgentMeta(agent: string): { agent: AgentName; title: string; emoji: string } {
    switch (agent) {
      case 'orchestrator':
        return { agent: 'orchestrator', title: 'Orchestrator Robot', emoji: '🤖' };
      case 'behavior_agent':
        return { agent: 'behavior_agent', title: 'Behavior Robot', emoji: '🧠' };
      case 'location_agent':
        return { agent: 'location_agent', title: 'Location Robot', emoji: '📡' };
      case 'merchant_agent':
        return { agent: 'merchant_agent', title: 'Merchant Robot', emoji: '🏪' };
      case 'device_agent':
        return { agent: 'device_agent', title: 'Device Robot', emoji: '💻' };
      case 'vpn_agent':
        return { agent: 'vpn_agent', title: 'VPN Robot', emoji: '🛡️' };
      case 'merge_node':
        return { agent: 'merge_node', title: 'Merge Node', emoji: '🧩' };
      case 'policy_node':
        return { agent: 'policy_node', title: 'Policy Node', emoji: '📘' };
      case 'confidence_node':
        return { agent: 'confidence_node', title: 'Confidence Node', emoji: '📏' };
      case 'action_node':
        return { agent: 'action_node', title: 'Action Node', emoji: '⚡' };
      case 'guardrail_node':
        return { agent: 'guardrail_node', title: 'Guardrail Node', emoji: '🧱' };
      case 'human_review':
      case 'hil_node':
        return { agent: 'human_review', title: 'Human Review', emoji: '🧑‍⚖️' };
      default:
        return { agent: 'system', title: 'System', emoji: '⚙️' };
    }
  }

  trackBySequence(_: number, item: ChatMessage): number {
    return item.sequence;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}