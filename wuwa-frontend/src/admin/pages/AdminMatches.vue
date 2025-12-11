<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const matches = ref([])
const form = ref({ id: null, team1: '', team2: '', score1: 0, score2: 0, date: '' })
const editing = ref(false)

async function load() {
  const res = await api.get('/matches')
  matches.value = res.data
}

function edit(match: any) {
  form.value = { ...match }
  editing.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/matches/${form.value.id}`, form.value)
  } else {
    await api.post('/matches', form.value)
  }
  form.value = { id: null, team1: '', team2: '', score1: 0, score2: 0, date: '' }
  editing.value = false
  load()
}

async function remove(id: number) {
  await api.delete(`/matches/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-content">
    <h1>Manage Matches</h1>

    <form class="edit-form fx-glow">
      <input v-model="form.team1" placeholder="Team 1" />
      <input v-model="form.team2" placeholder="Team 2" />
      <input v-model.number="form.score1" type="number" placeholder="Score 1" />
      <input v-model.number="form.score2" type="number" placeholder="Score 2" />
      <input v-model="form.date" type="datetime-local" placeholder="Date" />
      <button class="ww-btn" @click.prevent="save">{{ editing ? 'Update' : 'Create' }}</button>
    </form>

    <table class="table">
      <thead>
        <tr><th>Match</th><th>Score</th><th>Date</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="m in matches" :key="m.id">
          <td>{{ m.team1 }} vs {{ m.team2 }}</td>
          <td>{{ m.score1 }} - {{ m.score2 }}</td>
          <td>{{ m.date }}</td>
          <td>
            <button @click="edit(m)">Edit</button>
            <button @click="remove(m.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

