/**
 * Process Management Page
 * DO-178C Traceability: REQ-SM-001 to REQ-SM-006, REQ-FE-TBD (Process Management UI)
 * Purpose: View and manage development process state machines for Configuration Items
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

interface Phase {
  phase_id: string;
  name: string;
  order: number;
  status: string;
  current_sub_phase_index: number;
  entry_criteria_met: boolean;
  exit_criteria_met: boolean;
  started_at: string | null;
  completed_at: string | null;
  sub_phases: SubPhase[];
  deliverables: any[];
  reviews: any[];
}

interface SubPhase {
  sub_phase_id: string;
  name: string;
  order: number;
  status: string;
  current_activity_index: number;
  started_at: string | null;
  completed_at: string | null;
  activities: Activity[];
}

interface Activity {
  activity_id: string;
  name: string;
  activity_type: string;
  status: string;
  required: boolean;
  started_at: string | null;
  completed_at: string | null;
  output_artifacts: string[];
  completion_data: any;
}

interface StateMachine {
  state_machine_id: number;
  ci_id: number;
  template_id: string;
  template_name: string;
  dal_level: string | null;
  current_phase_index: number;
  state_data: {
    instance_id: string;
    ci_id: number;
    ci_type: string;
    template_id: string;
    template_name: string;
    dal_level: string | null;
    current_phase_index: number;
    created_at: string;
    updated_at: string;
    context: any;
    phases: Phase[];
  };
  created_at: string;
  updated_at: string;
}

interface Progress {
  ci_id: number;
  template_name: string;
  dal_level: string | null;
  total_phases: number;
  completed_phases: number;
  current_phase_index: number;
  total_activities: number;
  completed_activities: number;
  progress_percent: number;
  current_phase_name: string;
}

interface ConfigurationItem {
  id: number;
  ci_identifier: string;
  name: string;
  ci_type: string;
  criticality: string | null;
  status: string;
  has_state_machine?: boolean;
  progress?: Progress;
}

const ProcessManagement: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [configurationItems, setConfigurationItems] = useState<ConfigurationItem[]>([]);
  const [selectedCI, setSelectedCI] = useState<number | null>(null);
  const [stateMachine, setStateMachine] = useState<StateMachine | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [currentActivity, setCurrentActivity] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);

  // Fetch Configuration Items
  useEffect(() => {
    if (projectId) {
      fetchConfigurationItems();
    }
  }, [projectId]);

  const fetchConfigurationItems = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/configuration-items`);
      const items = response.data.items || [];

      // Fetch progress for each CI
      const itemsWithProgress = await Promise.all(
        items.map(async (item: ConfigurationItem) => {
          try {
            const progressResponse = await axios.get(`${API_BASE_URL}/configuration-items/${item.id}/progress`);
            return { ...item, has_state_machine: true, progress: progressResponse.data };
          } catch (err) {
            return { ...item, has_state_machine: false };
          }
        })
      );

      setConfigurationItems(itemsWithProgress);
      setError(null);
    } catch (err) {
      setError('Failed to load configuration items');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch State Machine for selected CI
  const fetchStateMachine = async (ciId: number) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/configuration-items/${ciId}/state-machine`);
      setStateMachine(response.data);

      // Also fetch progress and current activity
      const progressResponse = await axios.get(`${API_BASE_URL}/configuration-items/${ciId}/progress`);
      setProgress(progressResponse.data);

      try {
        const activityResponse = await axios.get(`${API_BASE_URL}/configuration-items/${ciId}/current-activity`);
        setCurrentActivity(activityResponse.data);
      } catch {
        setCurrentActivity(null);
      }

      setError(null);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setStateMachine(null);
        setProgress(null);
        setCurrentActivity(null);
      } else {
        setError('Failed to load state machine');
      }
    } finally {
      setLoading(false);
    }
  };

  // Create State Machine for a CI
  const createStateMachine = async (ciId: number) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/configuration-items/${ciId}/state-machine`, {
        auto_start: true
      });

      // Refresh data
      await fetchStateMachine(ciId);
      await fetchConfigurationItems();
      setError(null);
    } catch (err) {
      setError('Failed to create state machine');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Complete Activity
  const completeActivity = async (ciId: number, activityId: string) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/configuration-items/${ciId}/complete-activity`, {
        activity_id: activityId,
        completion_data: {
          completed_by: 'user',
          timestamp: new Date().toISOString()
        }
      });

      // Refresh state machine data
      await fetchStateMachine(ciId);
      await fetchConfigurationItems();
      setError(null);
    } catch (err) {
      setError('Failed to complete activity');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Skip Activity
  const skipActivity = async (ciId: number, activityId: string) => {
    const reason = prompt('Please provide a reason for skipping this activity:');
    if (!reason) return;

    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/configuration-items/${ciId}/skip-activity`, {
        activity_id: activityId,
        reason: reason
      });

      // Refresh state machine data
      await fetchStateMachine(ciId);
      await fetchConfigurationItems();
      setError(null);
    } catch (err) {
      setError('Failed to skip activity');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Select a CI
  const handleSelectCI = (ciId: number) => {
    setSelectedCI(ciId);
    fetchStateMachine(ciId);
  };

  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'blocked':
        return 'bg-red-100 text-red-800';
      case 'not_started':
        return 'bg-gray-100 text-gray-800';
      case 'skipped':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Render CI List
  const renderCIList = () => (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Configuration Items</h2>
      {configurationItems.length === 0 ? (
        <p className="text-gray-500">No configuration items found for this project.</p>
      ) : (
        <div className="space-y-2">
          {configurationItems.map((ci) => (
            <div
              key={ci.id}
              onClick={() => handleSelectCI(ci.id)}
              className={`p-4 border rounded cursor-pointer transition-colors ${
                selectedCI === ci.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold">{ci.name}</h3>
                  <p className="text-sm text-gray-500">{ci.ci_identifier}</p>
                  <div className="flex gap-2 mt-2">
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(ci.ci_type)}`}>
                      {ci.ci_type}
                    </span>
                    {ci.criticality && (
                      <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-800">
                        {ci.criticality}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  {ci.has_state_machine && ci.progress ? (
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {ci.progress.progress_percent}%
                      </div>
                      <p className="text-xs text-gray-500">
                        {ci.progress.completed_activities}/{ci.progress.total_activities} activities
                      </p>
                    </div>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        createStateMachine(ci.id);
                      }}
                      className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                    >
                      Start Process
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Render Current Activity Card
  const renderCurrentActivity = () => {
    if (!currentActivity) return null;

    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-6">
        <h3 className="font-bold text-lg mb-2">Current Activity</h3>
        <div className="text-sm space-y-1">
          <p><strong>Phase:</strong> {currentActivity.phase.name}</p>
          <p><strong>Sub-Phase:</strong> {currentActivity.sub_phase.name}</p>
          <p><strong>Activity:</strong> {currentActivity.activity.name}</p>
          <p><strong>Type:</strong> {currentActivity.activity.type}</p>
          {currentActivity.activity.output_artifacts.length > 0 && (
            <div>
              <strong>Expected Outputs:</strong>
              <ul className="list-disc ml-6">
                {currentActivity.activity.output_artifacts.map((artifact: string, idx: number) => (
                  <li key={idx}>{artifact}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="mt-4 flex gap-3">
          <button
            onClick={() => selectedCI && completeActivity(selectedCI, currentActivity.activity.activity_id)}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
          >
            ✓ Complete Activity
          </button>
          {!currentActivity.activity.required && (
            <button
              onClick={() => selectedCI && skipActivity(selectedCI, currentActivity.activity.activity_id)}
              disabled={loading}
              className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:bg-gray-400"
            >
              Skip (Optional)
            </button>
          )}
        </div>
      </div>
    );
  };

  // Render Progress Bar
  const renderProgressBar = () => {
    if (!progress) return null;

    return (
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-bold">Overall Progress</h3>
          <span className="text-2xl font-bold text-blue-600">{progress.progress_percent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-300"
            style={{ width: `${progress.progress_percent}%` }}
          ></div>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Phases</p>
            <p className="font-semibold">{progress.completed_phases} / {progress.total_phases}</p>
          </div>
          <div>
            <p className="text-gray-600">Activities</p>
            <p className="font-semibold">{progress.completed_activities} / {progress.total_activities}</p>
          </div>
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-600">Current Phase</p>
          <p className="font-semibold">{progress.current_phase_name}</p>
        </div>
      </div>
    );
  };

  // Render Phase Timeline
  const renderPhaseTimeline = () => {
    if (!stateMachine) return null;

    const phases = stateMachine.state_data.phases;

    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4">Development Process</h3>
        <p className="text-sm text-gray-600 mb-4">
          Template: {stateMachine.template_name}
          {stateMachine.dal_level && ` (${stateMachine.dal_level})`}
        </p>

        <div className="space-y-4">
          {phases.map((phase, phaseIdx) => (
            <div key={phase.phase_id} className="border rounded">
              <div
                onClick={() => setExpandedPhase(expandedPhase === phaseIdx ? null : phaseIdx)}
                className="p-4 cursor-pointer hover:bg-gray-50 flex justify-between items-center"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-400">
                      {phase.order + 1}
                    </span>
                    <div>
                      <h4 className="font-semibold">{phase.name}</h4>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(phase.status)}`}>
                        {phase.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>
                <svg
                  className={`w-5 h-5 transition-transform ${expandedPhase === phaseIdx ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              {expandedPhase === phaseIdx && (
                <div className="border-t p-4 bg-gray-50">
                  <h5 className="font-semibold mb-3">Sub-Phases</h5>
                  <div className="space-y-3">
                    {phase.sub_phases.map((subPhase) => (
                      <div key={subPhase.sub_phase_id} className="bg-white p-3 rounded border">
                        <div className="flex justify-between items-start mb-2">
                          <h6 className="font-medium">{subPhase.name}</h6>
                          <span className={`text-xs px-2 py-1 rounded ${getStatusColor(subPhase.status)}`}>
                            {subPhase.status.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="mt-2">
                          <p className="text-xs text-gray-600 mb-1">Activities:</p>
                          <div className="space-y-1">
                            {subPhase.activities.map((activity) => (
                              <div
                                key={activity.activity_id}
                                className="flex items-center gap-2 text-sm"
                              >
                                <div className={`w-4 h-4 rounded-full ${
                                  activity.status === 'completed' ? 'bg-green-500' :
                                  activity.status === 'in_progress' ? 'bg-blue-500' :
                                  activity.status === 'skipped' ? 'bg-yellow-500' :
                                  'bg-gray-300'
                                }`}></div>
                                <span className={activity.required ? '' : 'italic text-gray-500'}>
                                  {activity.name}
                                </span>
                                {!activity.required && (
                                  <span className="text-xs text-gray-400">(optional)</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {phase.deliverables.length > 0 && (
                    <div className="mt-4">
                      <h6 className="font-medium mb-2">Deliverables</h6>
                      <ul className="list-disc ml-6 text-sm text-gray-700">
                        {phase.deliverables.map((deliverable, idx) => (
                          <li key={idx}>{deliverable.name || deliverable}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {phase.reviews.length > 0 && (
                    <div className="mt-4">
                      <h6 className="font-medium mb-2">Reviews</h6>
                      <ul className="list-disc ml-6 text-sm text-gray-700">
                        {phase.reviews.map((review, idx) => (
                          <li key={idx}>{review.name || review}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Process Management</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: CI List */}
        <div className="lg:col-span-1">
          {renderCIList()}
        </div>

        {/* Right: State Machine Details */}
        <div className="lg:col-span-2">
          {selectedCI ? (
            <>
              {renderCurrentActivity()}
              {renderProgressBar()}
              {stateMachine ? (
                renderPhaseTimeline()
              ) : (
                <div className="bg-white shadow rounded-lg p-6 text-center">
                  <p className="text-gray-500 mb-4">No process started for this CI</p>
                  <button
                    onClick={() => createStateMachine(selectedCI)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Create Process State Machine
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white shadow rounded-lg p-6 text-center">
              <p className="text-gray-500">Select a Configuration Item to view its development process</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessManagement;
