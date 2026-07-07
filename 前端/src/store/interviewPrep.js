import { defineStore } from 'pinia'

export const useInterviewPrepStore = defineStore('interviewPrep', {
  state: () => ({
    candidateName: '',
    candidateSchool: '',
    candidateMajor: '',
    candidateGraduation: '',
    duration: '30分钟',
    difficulty: '中等',
    language: '普通话',
    jobId: null,
    jobName: '',
    skills: [],
    resumeFileName: '',
    projectExperience: '',
    extractedSkills: [],
    extractedProjects: []
  }),

  actions: {
    savePrepData({ candidate, interview, selectedId, selectedJobName, selectedSkills, resumeFileName, projectExperience }) {
      this.candidateName = candidate.name || ''
      this.candidateSchool = candidate.school || ''
      this.candidateMajor = candidate.major || ''
      this.candidateGraduation = candidate.graduation || ''

      this.duration = interview.duration
      this.difficulty = interview.difficulty
      this.language = interview.language

      this.jobId = selectedId
      this.jobName = selectedJobName || ''

      this.skills = [...selectedSkills]
      this.resumeFileName = resumeFileName || ''
      this.projectExperience = projectExperience || ''
    },

    setExtracted({ skills, projects }) {
      this.extractedSkills = [...skills]
      this.extractedProjects = [...projects]
    },

    reset() {
      this.$reset()
    }
  }
})
