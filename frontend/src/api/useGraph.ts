import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchJson } from './client.ts';
import { CompanyDetailResponse, CompanyNewsResponse, GraphResponse, NetworkType } from '../types/graph.ts';

export function useGraph(sector?: string | null, networkType: NetworkType = 'all') {
  return useQuery<GraphResponse>({
    queryKey: ['graph', sector ?? 'all', networkType],
    queryFn: () => {
      const params = new URLSearchParams();
      if (sector) params.append('sector', sector);
      if (networkType && networkType !== 'all') params.append('network_type', networkType);
      const queryStr = params.toString();
      const url = queryStr ? `/graph?${queryStr}` : '/graph';
      return fetchJson<GraphResponse>(url);
    },
    staleTime: 1000 * 60 * 5, // 5 mins
  });
}

export function useCompany(ticker?: string | null) {
  return useQuery<CompanyDetailResponse>({
    queryKey: ['company', ticker],
    queryFn: () => fetchJson<CompanyDetailResponse>(`/companies/${encodeURIComponent(ticker!)}`),
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 15,
  });
}

export function useCompanyNews(ticker?: string | null) {
  return useQuery<CompanyNewsResponse>({
    queryKey: ['company-news', ticker],
    queryFn: () => fetchJson<CompanyNewsResponse>(`/companies/${encodeURIComponent(ticker!)}/news`),
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10, // 10 minutes cache
  });
}

export function useRefreshCompanyNews() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ticker: string) =>
      fetchJson<CompanyNewsResponse>(`/companies/${encodeURIComponent(ticker)}/news?force_refresh=true`),
    onSuccess: (data, ticker) => {
      queryClient.setQueryData(['company-news', ticker], data);
    },
  });
}
