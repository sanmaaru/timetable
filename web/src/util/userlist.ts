import {UserInfo} from "../types/account";
import {filter} from "lodash";

export type SortOption = 'desc' | 'asc';
export type SortClass = 'name' | 'username' | 'email' | 'generation' | 'class' | 'number';

export interface SortConfig {
    clazz: SortClass,
    option: SortOption
}

const propertyMap: Record<SortClass, keyof UserInfo> = {
    name: 'name',
    username: 'username',
    email: 'email',
    generation: 'generation',
    class: 'clazz',
    number: 'number'
};

export function sortUserInfos(userInfos: UserInfo[], sortConfig: SortConfig) {
    const { clazz, option } = sortConfig;
    const targetKey = propertyMap[clazz];
    const isAsc = option === 'asc'
    if (!userInfos || !Array.isArray(userInfos) || userInfos.length === 0) {
        return [];
    }

    return [...userInfos].sort((a, b) => {
        const valueA = a[targetKey];
        const valueB = b[targetKey];

        if (valueA === undefined || valueA === null) return isAsc ? 1 : -1;
        if (valueB === undefined || valueB === null) return isAsc ? -1 : 1;

        if (typeof valueA === 'string' && typeof valueB === 'string') {
            const comparison = valueA.localeCompare(valueB);
            return isAsc ? comparison : -comparison;
        }

        if (valueA > valueB) return isAsc ? -1 : 1;
        if (valueA < valueB) return isAsc ? 1 : -1;
        return 0;
    })
}

export interface FilterConfig {
    generation?: number;
    clazz?: number;
    isJoined?: boolean;
    searchKeyword: string;
}

export function filterUserInfos(userInfos: UserInfo[], filterConfig: FilterConfig) {
    return [...userInfos].filter((userInfo) => {
        let predicate = true
        if(filterConfig.generation != undefined)
            predicate = predicate && (userInfo.generation == filterConfig.generation)

        if(filterConfig.clazz != undefined)
            predicate = predicate && (userInfo.clazz == filterConfig.clazz)

        if(filterConfig.isJoined != undefined)
            predicate = predicate && ((userInfo.userId != null) == filterConfig.isJoined)

        if(filterConfig.searchKeyword) {
            const keyword = filterConfig.searchKeyword.toLowerCase();
            const matchSearch =
                (userInfo.name?.toLowerCase().includes(keyword)) ||
                (userInfo.username?.toLowerCase().includes(keyword)) ||
                (userInfo.email?.toLowerCase().includes(keyword));
            predicate = predicate && matchSearch;
        }

        return predicate
    })
}