<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const schedule = ref([])
const form = ref({ id: null, match_id: '', date: '', location: '' })
const editing = ref(false)

async function load() {
  const res = await api.get('/schedule')
  schedule.value = res.data
}

function edit(item: any) {
  form.value = { ...item }
  editing.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/schedule/${form.value.id}`, form.value)
  } else {
    await api.post('/schedule', form.value)
  }
  form.value = { id: null, match_id: '', date: '', location: '' }
  editing.value = false
  load()
}

async function remove(id: number) {
  await api.delete(`/schedule/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-content">
    <h1>Manage Schedule</h1>

    <form class="edit-form fx-glow">
      <input v-model="form.match_id" placeholder="Match ID / Teams" />
      <input v-model="form.date" type="datetime-local" placeholder="Date" />
      <input v-model="form.location" placeholder="Location" />
      <button class="ww-btn" @click.prevent="save">{{ editing ? 'Update' : 'Create' }}</button>
    </form>

    <table class="table">
      <thead>
        <tr><th>Match</th><th>Date</th><th>Location</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="s in schedule" :key="s.id">
          <td>{{ s.match_id }}</td>
          <td>{{ s.date }}</td>
          <td>{{ s.location }}</td>
          <td>
            <button @click="edit(s)">Edit</button>
            <button @click="remove(s.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

