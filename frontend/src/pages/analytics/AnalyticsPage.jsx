/**
 * AnalyticsPage Component
 * Comprehensive analytics dashboard with charts and metrics
 */

import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  CpuChipIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { Card, Loading } from '@components/ui';
import { LineChart, BarChart, PieChart, AreaChart } from '@components/ui/Charts';
import { analyticsService } from '@services';
import { formatNumber, formatCurrency, formatDuration } from '@utils/formatters';
import toast from 'react-hot-toast';

/**
 * Stat Card Component
 */
function StatCard({ title, value, change, icon: Icon, trend, color = 'blue' }) {
  const isPositive = change >= 0;
  const TrendIcon = isPositive ? ArrowTrendingUpIcon : ArrowTrendingDownIcon;

  return (
    <Card>
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            {change !== undefined && (
              <div className="flex items-center gap-1 mt-2">
                <TrendIcon
                  className={`w-4 h-4 ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}
                />
                <span
                  className={`text-sm font-medium ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {Math.abs(change)}%
                </span>
                <span className="text-sm text-gray-500">vs last period</span>
              </div>
            )}
          </div>
          <div
            className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center flex-shrink-0`}
          >
            <Icon className={`w-6 h-6 text-${color}-600`} />
          </div>
        </div>
      </div>
    </Card>
  );
}

/**
 * AnalyticsPage Component
 */
export default function AnalyticsPage() {
  const dispatch = useDispatch();

  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');
  const [overview, setOverview] = useState(null);
  const [workflowStats, setWorkflowStats] = useState([]);
  const [executionTrends, setExecutionTrends] = useState([]);
  const [aiUsageData, setAIUsageData] = useState([]);
  const [errorStats, setErrorStats] = useState([]);

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  /**
   * Load analytics data
   */
  const loadAnalytics = async () => {
    try {
      setLoading(true);

      // In a real app, this would fetch from the API
      // For now, we'll use mock data
      setOverview({
        totalExecutions: 1248,
        executionsChange: 12.5,
        successRate: 94.2,
        successRateChange: 2.1,
        avgDuration: 3456,
        avgDurationChange: -8.3,
        aiCalls: 4892,
        aiCallsChange: 15.7,
        totalCost: 127.45,
        costChange: 10.2,
      });

      setWorkflowStats([
        { name: 'Email Automation', executions: 452, success: 98 },
        { name: 'Data Extraction', executions: 328, success: 92 },
        { name: 'Report Generation', executions: 234, success: 96 },
        { name: 'Lead Processing', executions: 134, success: 89 },
        { name: 'Content Summarization', executions: 100, success: 95 },
      ]);

      setExecutionTrends([
        { date: '2024-01-01', successful: 45, failed: 3 },
        { date: '2024-01-02', successful: 52, failed: 2 },
        { date: '2024-01-03', successful: 48, failed: 4 },
        { date: '2024-01-04', successful: 61, failed: 2 },
        { date: '2024-01-05', successful: 55, failed: 5 },
        { date: '2024-01-06', successful: 67, failed: 3 },
        { date: '2024-01-07', successful: 58, failed: 2 },
      ]);

      setAIUsageData([
        { category: 'Summarization', calls: 1842, cost: 45.32 },
        { category: 'Extraction', calls: 1456, cost: 38.91 },
        { category: 'Classification', calls: 892, cost: 22.14 },
        { category: 'Generation', calls: 702, cost: 21.08 },
      ]);

      setErrorStats([
        { type: 'Timeout', count: 12 },
        { type: 'API Error', count: 8 },
        { type: 'Invalid Input', count: 6 },
        { type: 'Rate Limit', count: 4 },
        { type: 'Other', count: 3 },
      ]);
    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading.LoadingPage />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">
            Monitor performance and track usage metrics
          </p>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center gap-2">
          {[
            { value: '24h', label: '24 Hours' },
            { value: '7d', label: '7 Days' },
            { value: '30d', label: '30 Days' },
            { value: '90d', label: '90 Days' },
          ].map((range) => (
            <button
              key={range.value}
              onClick={() => setTimeRange(range.value)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                timeRange === range.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="Total Executions"
          value={formatNumber(overview.totalExecutions)}
          change={overview.executionsChange}
          icon={ChartBarIcon}
          color="blue"
        />

        <StatCard
          title="Success Rate"
          value={`${overview.successRate}%`}
          change={overview.successRateChange}
          icon={ArrowTrendingUpIcon}
          color="green"
        />

        <StatCard
          title="Avg Duration"
          value={formatDuration(overview.avgDuration)}
          change={overview.avgDurationChange}
          icon={ClockIcon}
          color="purple"
        />

        <StatCard
          title="AI API Calls"
          value={formatNumber(overview.aiCalls)}
          change={overview.aiCallsChange}
          icon={CpuChipIcon}
          color="indigo"
        />

        <StatCard
          title="Total Cost"
          value={formatCurrency(overview.totalCost)}
          change={overview.costChange}
          icon={CurrencyDollarIcon}
          color="yellow"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Execution Trends */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Execution Trends
            </h3>
            <AreaChart
              data={executionTrends}
              xKey="date"
              yKeys={[
                { key: 'successful', color: '#10b981', name: 'Successful' },
                { key: 'failed', color: '#ef4444', name: 'Failed' },
              ]}
              height={300}
            />
          </div>
        </Card>

        {/* Top Workflows */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Top Workflows by Executions
            </h3>
            <BarChart
              data={workflowStats}
              xKey="name"
              yKey="executions"
              color="#3b82f6"
              height={300}
            />
          </div>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Usage Breakdown */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              AI Usage by Category
            </h3>
            <PieChart
              data={aiUsageData.map((item) => ({
                name: item.category,
                value: item.calls,
              }))}
              height={300}
            />
            <div className="mt-4 space-y-2">
              {aiUsageData.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-600">{item.category}</span>
                  <div className="flex items-center gap-3">
                    <span className="font-medium">
                      {formatNumber(item.calls)} calls
                    </span>
                    <span className="text-gray-500">
                      {formatCurrency(item.cost)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Error Distribution */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Error Distribution
            </h3>
            <PieChart
              data={errorStats.map((item) => ({
                name: item.type,
                value: item.count,
              }))}
              height={300}
            />
            <div className="mt-4 space-y-2">
              {errorStats.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-600">{item.type}</span>
                  <span className="font-medium">{item.count} errors</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Workflow Performance Table */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Workflow Performance
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Workflow
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Executions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {workflowStats.map((workflow, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {workflow.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatNumber(workflow.executions)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm text-gray-900 mr-2">
                          {workflow.success}%
                        </div>
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${workflow.success}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDuration(2000 + index * 500)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </div>
  );
}
