import React, {ChangeEvent, useCallback, useEffect, useState} from 'react';
import style from './UserManagement.module.css';
import {useUserInfos} from "../../hooks/useUser";
import _ from 'lodash';
import FloatingMenu from "../../components/menu/FloatingMenu";
import useFloatingMenu from "../../hooks/useFloatingMenu";
import {RadioButton, RadioButtonList} from "../../components/Input/RadioButtonList";
import {FilterConfig, SortClass, SortConfig, SortOption} from "../../util/userlist";
import {UserList} from "../../components/management/UserList";
import {DropdownChip} from "../../components/Input/DropdownChip";
import {getGeneration} from "../../util/common";

export const SECTION_LIST = ['student', 'teacher', 'manager', 'admin'] as const
export type Section = typeof SECTION_LIST[number];

// ===== Constants For Section =====
interface SectionButton {
    section: Section;
    title: string;
}

const sectionButtons: SectionButton[] = [
    { title: 'Students', section: 'student' },
    { title: 'Teachers', section: 'teacher' },
    { title: 'Managers', section: 'admin' },
]

// ===== Constants For Sorting =====
const sortClassButtons: RadioButton<SortClass>[] = [
    { label: '이름' , value: 'name' },
    { label: '사용자이름' , value: 'username' },
    { label: '이메일' , value: 'email' },
    { label: '기수' , value: 'generation' },
    { label: '반' , value: 'class' },
    { label: '번호' , value: 'number' }
]

const managerSortClassButtons: RadioButton<SortClass>[] = [
    { label: '이름' , value: 'name' },
    { label: '사용자이름' , value: 'username' },
    { label: '이메일' , value: 'email' }
]

const sortOptionButtons: RadioButton<SortOption>[] = [
    { label: '오름차순', value: 'asc', icon: '↑' },
    { label: '내림차순', value: 'desc', icon: '↓' },
]

// ===== Constants For Filtering =====
const generationOption = [undefined, 1, 2, 3].map((value) => {
    if(!value)
        return { label: '사용안함', value: value }
    return { label: `${getGeneration(value)}기`, value: value }
});
const classOption = [undefined, 1, 2, 3, 4, 5, 6].map((value) => {
    if(!value)
        return { label: '사용안함', value: value }
    return { label: `${value}반`, value: value }
})
const joinedOption = [undefined, true, false].map((value) => {
    if(value == undefined)
        return { label: '사용안함', value: value }
    return { label: value ? '가입함' : '가입안함', value: value }
})

const UserManagement = () => {
    const [currentSection, setCurrentSection] = useState<Section>('student')
    const { userInfos } = useUserInfos(currentSection)
    const [sortOption, setSortOption] = useState<SortConfig>({ clazz: 'name', option: 'desc' })
    const [isSortMenuOpen, setSortMenuOpen] = useState(false)
    const {
        ref: sortRef,
        menuContext: sortMenuContext,
        getReferenceProps: getSortReferenceProps
    } = useFloatingMenu(isSortMenuOpen, setSortMenuOpen)
    const [filterOption, setFilterOption] = useState<FilterConfig>({ searchKeyword: '' });
    const [isFilterMenuOpen, setFilterMenuOpen] = useState(false)
    const {
        ref: filterRef,
        menuContext: filterMenuContext,
        getReferenceProps: getFilterReferenceProps
    } = useFloatingMenu(isFilterMenuOpen, setFilterMenuOpen)

    const debouncedSearch = useCallback(
        _.debounce((query: string) => {
            setFilterOption((prev) => { return {...prev, searchKeyword: query}})
        }, 300)
        ,[]);

    const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        debouncedSearch(value);
    }

    // clear filter option of student when change section to manager
    useEffect(() => {
        if(currentSection !== 'student') {
            setFilterOption((prev) => {
                return {
                    generation: undefined,
                    clazz: undefined,
                    number: undefined,
                    isJoined: prev.isJoined,
                    searchKeyword: prev.searchKeyword
                }
            })
        }
    }, [currentSection])


    return (
        <div className={style.userManagementPage}>
            <span>유저 관리</span>
            <div className={style.container}>
                <div className={style.sectionBtnArea}>
                    {sectionButtons.map(({title, section}) =>
                        <button
                            className={`${style.sectionBtn} ${currentSection === section ? style.active : ''}`}
                            onClick={() => setCurrentSection(section)}
                            key={section}
                        >
                            {title}
                        </button>
                    )}
                </div>
                <div className={style.searchContainer}>
                    <div className={style.searchBox}>
                        <input
                            type='text'
                            placeholder='Search...'
                            className={style.searchInput}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div className={style.viewOptionMenu}>
                        <button
                            className={style.viewOptionButton}
                            ref={sortRef}
                            {...getSortReferenceProps()}
                        >
                            Sort By
                        </button>
                    </div>
                    <div className={style.viewOptionMenu}>
                        <button
                            className={style.viewOptionButton}
                            ref={filterRef}
                            {...getFilterReferenceProps()}
                        >
                            Filter By
                        </button>
                    </div>
                </div>
                <div className={style.border}></div>
                <UserList
                    className={style.userList}
                    section={currentSection}
                    userInfos={userInfos}
                    sortConfig={sortOption}
                    filterConfig={filterOption}
                />
            </div>
            {sortMenuContext.isMounted && (
                <FloatingMenu context={sortMenuContext}>
                    <div className={style.sortMenu}>
                        <span>Sort By</span>
                        <div>
                            <RadioButtonList
                                buttons={currentSection === 'student' ? sortClassButtons : managerSortClassButtons}
                                currentOption={sortOption.clazz}
                                onOptionChange={(e) => {
                                    setSortOption((prev) => {
                                        return { clazz: e, option: prev.option }
                                    })
                                }}
                            />
                        </div>
                        <div>
                            <RadioButtonList
                                buttons={sortOptionButtons}
                                currentOption={sortOption.option}
                                onOptionChange={(e) => {
                                    setSortOption((prev) => {
                                        return { clazz: prev.clazz, option: e }
                                    })
                                }}
                                variant={'icon'}
                            />
                        </div>
                    </div>
                </FloatingMenu>
            )}
            {filterMenuContext.isMounted && (
                <FloatingMenu context={filterMenuContext}>
                    <div className={style.filterMenu}>
                        <span>Filter By</span>
                        {(currentSection === 'student') && (<div className={style.filterOption}>
                            <span>반</span>
                            <DropdownChip
                                options={classOption}
                                currentOption={filterOption.clazz}
                                onOptionChange={(value) => {
                                    setFilterOption((prev) => {
                                        return {...prev, clazz: value}
                                    })
                                }}
                                icon={false}
                            />
                        </div>)}
                        {(currentSection === 'student') && (<div className={style.filterOption}>
                            <span>기수</span>
                            <DropdownChip
                                options={generationOption}
                                currentOption={filterOption.generation}
                                onOptionChange={(value) => {
                                    setFilterOption((prev) => { return {...prev, generation: value}})
                                }}
                                icon={false}
                            />
                        </div>)}
                        {(currentSection === 'student') && (<div className={style.divider}></div>)}
                        <div className={style.filterOption}>
                            <span>가입 여부</span>
                            <DropdownChip
                                options={joinedOption}
                                currentOption={filterOption.isJoined}
                                onOptionChange={(value) => {
                                    setFilterOption((prev) => { return {...prev, isJoined: value}})
                                }}
                                icon={false}
                            />
                        </div>
                    </div>
                </FloatingMenu>
            )}
        </div>
    )
};

export default UserManagement;
