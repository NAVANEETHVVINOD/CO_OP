import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/(app)/dashboard/page';

// Mock the dashboard widgets that might not be available
vi.mock('@/components/dashboard/CreditWidget', () => ({
  CreditWidget: () => <div>Credit Widget</div>,
}));

vi.mock('@/components/dashboard/SimulationToggle', () => ({
  SimulationToggle: () => <div>Simulation Toggle</div>,
}));

vi.mock('@/components/dashboard/ProjectsWidget', () => ({
  ProjectsWidget: () => <div>Projects Widget</div>,
}));

vi.mock('@/components/dashboard/InvoicesWidget', () => ({
  InvoicesWidget: () => <div>Invoices Widget</div>,
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders page header', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('System status and activity summary')).toBeInTheDocument();
  });

  it('displays loading skeletons initially', () => {
    const { container } = render(<DashboardPage />);
    const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('loads and displays document count', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Documents')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('loads and displays conversation count', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Conversations')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  it('displays health status indicators', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('System Snapshot')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Postgres')).toBeInTheDocument();
      expect(screen.getByText('Redis')).toBeInTheDocument();
      expect(screen.getByText('Qdrant')).toBeInTheDocument();
      expect(screen.getByText('MinIO')).toBeInTheDocument();
    });
  });

  it('displays recent activity section', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
  });

  it('shows activity entries', () => {
    render(<DashboardPage />);
    const uploadEntries = screen.getAllByText('UPLOAD');
    expect(uploadEntries.length).toBeGreaterThan(0);
    const searchEntries = screen.getAllByText('SEARCH');
    expect(searchEntries.length).toBeGreaterThan(0);
    expect(screen.getByText('CHAT')).toBeInTheDocument();
  });

  it('calculates estimated vectors from document count', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Vectors')).toBeInTheDocument();
    });

    await waitFor(() => {
      // 2 documents * 40 = ~80 vectors
      expect(screen.getByText('~80')).toBeInTheDocument();
    });
  });

  it('displays backend API URL', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Backend:')).toBeInTheDocument();
    });
  });
});
