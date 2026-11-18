import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchJson } from './client.ts';
import { ComparisonResponse, CountryInfo, DashboardResponse, RefreshResponse } from '../types/macro.ts';

export function useCountries() {
  return useQuery<CountryInfo[]>({
    queryKey: ['countries'],
    queryFn: () => fetchJson<CountryInfo[]>('/countries'),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useDashboard(countryCode: string) {
  return useQuery<DashboardResponse>({
    queryKey: ['dashboard', countryCode],
    queryFn: () => fetchJson<DashboardResponse>(`/dashboard/${encodeURIComponent(countryCode)}`),
    enabled: Boolean(countryCode),
    staleTime: 1000 * 60 * 5, // 5 mins
  });
}

export function useComparison(countries: string[], indicator: string, startYear?: string) {
  return useQuery<ComparisonResponse>({
    queryKey: ['compare', countries.join(','), indicator, startYear ?? 'all'],
    queryFn: () => {
      const params = new URLSearchParams({
        countries: countries.join(','),
        indicator,
      });
      if (startYear) params.append('start_year', startYear);
      return fetchJson<ComparisonResponse>(`/compare?${params.toString()}`);
    },
    enabled: countries.length > 0 && Boolean(indicator),
    staleTime: 1000 * 60 * 5,
  });
}

export function useRefreshDashboard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (countryCode: string) =>
      fetchJson<RefreshResponse>(`/refresh/${encodeURIComponent(countryCode)}`, { method: 'POST' }),
    onSuccess: (_, countryCode) => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', countryCode] });
    },
  });
}
